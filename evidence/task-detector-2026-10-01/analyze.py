"""Explain the datalink detector using retained development logs, without new runs.

Use --extract with the existing SITL Python environment to reproduce the ULog
extraction. The default report needs only Python's standard library.
"""
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RUNS = {
    name: ROOT / 'evidence/task-runtime-2026-09-29/runs' / name
    for name in ('corrected-instrumented', 'corrected-original-binary')
}
RUNS['full-parameters'] = ROOT / 'evidence/task-parameters-2026-09-30/run'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract():
    from pyulog import ULog
    runs = {}
    fields = {'telemetry_status': ['heartbeat_type_gcs'],
              'vehicle_status': ['gcs_connection_lost', 'nav_state'],
              'failsafe_flags': ['gcs_connection_lost']}
    for name, path in RUNS.items():
        ulog = ULog(io.BytesIO(gzip.decompress((path / 'flight.ulg.gz').read_bytes())),
                    message_name_filter_list=list(fields))
        raw = [json.loads(line) for line in gzip.decompress((path / 'raw.jsonl.gz').read_bytes()).splitlines()]
        injection = next(r for r in raw if r.get('name') == 'injection')
        topics = []
        for d in ulog.data_list:
            keys = ['timestamp', *fields[d.name]]
            topics.append(dict(name=d.name, instance=d.multi_id, fields=keys,
                               rows=[[int(d.data[k][i]) for k in keys]
                                     for i in range(len(d.data['timestamp']))]))
        runs[name] = dict(
            input_sha256={str((path / f).relative_to(ROOT)): sha(path / f)
                          for f in ('flight.ulg.gz', 'raw.jsonl.gz')},
            injection_cached_vehicle_us=round(injection['t_vehicle_s'] * 1e6),
            parameters={k: ulog.initial_parameters[k] for k in ('COM_DL_LOSS_T', 'COM_FAIL_ACT_T')},
            timing_parameter_changes=[list(change) for change in ulog.changed_parameters
                                      if change[1] in ('COM_DL_LOSS_T', 'COM_FAIL_ACT_T')],
            topics=topics)
    return runs


def generate():
    runs = json.loads((HERE / 'observations.json').read_text())
    report = {}
    native = json.loads((ROOT / 'evidence/task-runtime-2026-09-29/results.json').read_text())
    for name, run in runs.items():
        injection = run['injection_cached_vehicle_us']
        topics = run['topics']
        status = next(t['rows'] for t in topics if t['name'] == 'vehicle_status')
        flags = next(t['rows'] for t in topics if t['name'] == 'failsafe_flags')
        lost = next(t for t, loss, _ in status if t >= injection and loss)
        flag = next(t for t, loss in flags if t >= injection and loss)
        rtl = next(t for t, _, mode in status if t >= lost and mode == 5)
        links = []
        timeout = round(run['parameters']['COM_DL_LOSS_T'] * 1e6)
        for topic in topics:
            if topic['name'] != 'telemetry_status':
                continue
            true_times = [t for t, present in topic['rows'] if present and t < lost]
            if not true_times:
                continue
            last_true = max(true_times)
            first_false = next(t for t, present in topic['rows'] if t > last_true and not present)
            links.append(dict(instance=topic['instance'], last_logged_gcs_present_us=last_true,
                              first_logged_gcs_absent_us=first_false,
                              status_loss_after_last_logged_present_us=lost-last_true,
                              loss_between_logged_endpoints_plus_timeout=
                              last_true + timeout < lost <= first_false + timeout))
        report[name] = dict(
            parameters=run['parameters'], timing_parameter_changes=run['timing_parameter_changes'],
            injection_cached_lower_bound_us=injection,
            first_status_loss_us=lost, first_logged_loss_flag_us=flag, first_rtl_us=rtl,
            rtl_minus_cached_injection_us=rtl-injection,
            status_loss_to_rtl_us=rtl-lost, links=links,
            exact_last_received_heartbeat_us=None,
            exact_last_commander_timer_refresh_us=None,
            timing_verdict='inconclusive: injection upper bound and prospective tolerance absent')
        if name == 'corrected-instrumented':
            n = native['runs'][name]
            report[name]['native_consumed_flag_to_selected_rtl_us'] = (
                n['first_selected_rtl_us'] - n['first_consumed_armed_gcs_loss_us'])
    return dict(
        classification='guard-input timing assumption omitted MAVLink heartbeat qualification and status publication',
        runs=report,
        input_sha256={**{p: digest for r in runs.values() for p, digest in r['input_sha256'].items()},
                      'evidence/task-runtime-2026-09-29/results.json':
                      sha(ROOT / 'evidence/task-runtime-2026-09-29/results.json')},
        analysis_sha256={p.name: sha(p) for p in (HERE / 'analyze.py', HERE / 'observations.json', HERE / 'source.json')})


if __name__ == '__main__':
    print(json.dumps(extract() if '--extract' in sys.argv else generate(), indent=1))

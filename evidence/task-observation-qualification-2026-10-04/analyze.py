"""Reproduce the registered development pair from its external raw cache."""
import hashlib
import json
from pathlib import Path
import re
import runpy
import sys

HERE = Path(__file__).resolve().parent
PUBLIC = runpy.run_path(str(HERE.parent / 'task-public-flight-2026-10-04/analyze.py'))
SUMMARIZE_TOPIC = PUBLIC['summarize_topic']
NATIVE_SUMMARY = runpy.run_path(str(HERE.parent / 'task-runtime-2026-09-29/analyze.py'))['summarize']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def time_records(console):
    records = {}
    for stage, fields in re.findall(r'UAV_TIME (\w+) ([^\r\n]*)', console):
        row = {k: int(v) for k, v in re.findall(r'(\w+)=(-?\d+)', fields)}
        records.setdefault(stage, []).append(row)
    return records


def first_change(changes, value, after=0):
    return next((r for r in changes if r['value'] == value and r['first_sample_us'] >= after), None)


def native_timing(records, after):
    detector = next((r for r in records.get('detector', []) if r.get('lost') == 1 and r['t'] >= after), None)
    if detector is None:
        return None
    receives = [r for r in records.get('rx', []) if r['t'] <= detector['t']]
    last_rx = max(receives, key=lambda r:r['t']) if receives else None
    age = next((r for r in records.get('age', []) if last_rx and r.get('ch') == last_rx['ch']
                and r.get('last') == last_rx['t'] and r.get('gcs') == 0 and r['t'] >= last_rx['t']), None)
    anchor_publications = [r for r in records.get('telem', []) if r.get('gcs') == 1 and r['t'] == detector.get('anchor')]
    false_publication = next((r for r in records.get('telem', []) if age and r.get('ch') == age['ch']
                              and r.get('gcs') == 0 and r['t'] >= age['t']), None)
    hold = next((r for r in records.get('selected', []) if r.get('action') == 5 and r['t'] >= detector['t']), None)
    rtl = next((r for r in records.get('selected', []) if r.get('action') == 6 and r['t'] >= detector['t']), None)
    navigator = next((r for r in records.get('navigator', []) if rtl and r.get('mode') == 5 and r['t'] >= rtl['t']), None)
    return dict(last_observed_qualifying_receive=last_rx, first_observed_aged_false=age,
                receive_channels=sorted({r['ch'] for r in receives}),
                publications_matching_detector_anchor=anchor_publications,
                first_false_telemetry_publication=false_publication,
                first_lost_detector_bracket=detector, first_selected_hold=hold,
                first_selected_rtl=rtl, first_navigator_rtl_execution_bracket=navigator,
                receive_to_detector_interval_us=None if not last_rx else
                    [detector['t']-last_rx['t'], detector['end']-last_rx['t']],
                receive_to_selected_rtl_us=None if not last_rx or not rtl else rtl['t']-last_rx['t'],
                clock_limit='HRT is quantized by SIH lockstep. Equal entry/exit stamps do not prove zero host execution time. The observed receive is not the host cut instant.',
                commit_marker_limit='UAV_TIME commit follows nav field assignment but precedes nav_state_timestamp assignment; use the ULog nav_state_timestamp for that official stamp.')


def run_observations(run):
    from pyulog import ULog
    raw = [json.loads(line) for line in (run / 'raw.jsonl').read_text().splitlines()]
    launch = next(r for r in raw if r.get('kind') == 'launch')
    injection = next((r for r in raw if r.get('name') == 'injection'), None)
    snapshot = json.loads((run / 'parameters-full.json').read_text())
    trace = json.loads((run / 'trace.json').read_text())
    assert trace['identity']['execution']['raw_artifacts']['parameters-full.json'] == sha(run / 'parameters-full.json')
    fields = {
        'failsafe_flags': PUBLIC['FLAGS'], 'vehicle_status': PUBLIC['FIELDS']['vehicle_status'],
        'navigator_status': ['nav_state', 'failure'], 'telemetry_status': ['heartbeat_type_gcs'],
        'vehicle_local_position': ['xy_valid', 'z_valid'],
        'position_setpoint_triplet': ['current.valid', 'current.type'],
        'sensor_baro': [], 'sensor_mag': [], 'sensor_gps': [],
        'vehicle_global_position_groundtruth': [], 'cpuload': [],
    }
    ulog = ULog(str(run / 'flight.ulg'))
    topics, cpu = {}, {}
    for d in ulog.data_list:
        if d.name in fields and len(d.data['timestamp']):
            topics[f'{d.name}/{d.multi_id}'] = SUMMARIZE_TOPIC(d.data, fields[d.name], 0)
        if d.name == 'cpuload':
            for field in ['load', 'ram_usage']:
                if field in d.data:
                    values = [float(v) for v in d.data[field]]
                    cpu[field] = dict(min=min(values), mean=sum(values)/len(values), max=max(values))
    console = (run / 'px4.log').read_text()
    native = NATIVE_SUMMARY(run) if injection else None
    timing = {}
    if injection:
        threshold = injection['t_vehicle_s'] * 1e6
        flag = first_change(topics['failsafe_flags/0']['changes']['gcs_connection_lost'], 1, threshold)
        rtl = first_change(topics['vehicle_status/0']['changes']['nav_state'], 5, threshold)
        navigator = first_change(topics['navigator_status/0']['changes']['nav_state'], 5, threshold)
        timing = dict(host_injection_elapsed_s=injection['t_host_s'],
                      cached_vehicle_injection_interval_us=[round(threshold), None],
                      sampled_flag_rise=flag, rtl_mode_change=rtl, navigator_rtl=navigator,
                      logged_flag_to_rtl_commit_us=None if not flag or not rtl else rtl['commit_us']-flag['first_sample_us'],
                      sampled_flag_to_commit_interval_us=None if not flag or not rtl else
                          [rtl['commit_us']-flag['first_sample_us'], rtl['commit_us']-flag['previous_sample_us']],
                      commit_to_navigator_report_us=None if not rtl or not navigator else navigator['first_sample_us']-rtl['commit_us'])
    time_rows = time_records(console)
    if injection:
        timing['native_segments'] = native_timing(time_rows, threshold)
    return dict(summary=json.loads((run / 'summary.json').read_text()),
                stages=[r for r in raw if r.get('kind') == 'stage'],
                failures=[r for r in raw if r.get('kind') == 'failure'],
                binary_sha256=launch['executable_sha256'], instrumentation=launch['build_identity']['instrumentation'],
                snapshot_complete=snapshot['complete'], parameter_count=len(snapshot['parameters']),
                registry_sha256=snapshot['registry_sha256'], injection_observed=injection is not None,
                clock='PX4 HRT microseconds on this boot; host elapsed seconds are separate. No cross-clock upper bound.',
                topics=topics, cpu_observed=cpu,
                cpu_measurement_available=False,
                cpu_limit='Pinned LoadMon.cpp has no Darwin load/RAM calculation branch; zero-initialized fields are published. The recorded zeros cannot bound CPU cost.',
                ulog_dropouts=[dict(t_us=int(d.timestamp), duration_ms=int(d.duration)) for d in ulog.dropouts],
                uav_time_records={stage: dict(count=len(rows), first=rows[0], last=rows[-1],
                    max_adjacent_t_gap_us=max((b['t']-a['t'] for a,b in zip(rows, rows[1:]) if 't' in a and 't' in b), default=None))
                    for stage, rows in time_rows.items()},
                native=native, timing=timing,
                backpressure_limit='ULog dropouts and sampled CPU load do not measure every console/uORB queue wait or blocked callback.',
                raw_sha256={p.name:sha(p) for p in sorted(run.iterdir()) if p.is_file()})


def generate(cache):
    paths = {name: next((cache / name).glob('*/summary.json')).parent
             for name in ['clean-control', 'clean-instrumented']}
    runs = {name:run_observations(path) for name,path in paths.items()}
    snapshots = {name:json.loads((path/'parameters-full.json').read_text())['parameters'] for name,path in paths.items()}
    names = set().union(*(p.keys() for p in snapshots.values()))
    differences = [k for k in sorted(names) if snapshots['clean-control'].get(k) != snapshots['clean-instrumented'].get(k)]
    return dict(evidence_state='executed development observation qualification',
                attempts=len(runs), injected_runs=sum(r['injection_observed'] for r in runs.values()),
                valid_runs=sum(r['summary']['valid']['valid'] for r in runs.values()),
                confirmation_runs=0, logger_alternative_runs=0, agreement_verdict=None,
                timing_pass_fail=False, calibrated_tolerance=None,
                parameter_differences=differences,
                same_discrete_transition_sequence=(runs['clean-control']['summary']['transitions'] ==
                                                   runs['clean-instrumented']['summary']['transitions']),
                runs=runs,
                interpretation='A matched fresh-build pair does not identify compiler-cache staleness or a specific scheduling cause. Apply the qualification and protocol gates before any confirmation.',
                analyzer_sha256=sha(Path(__file__)),
                reused_analysis_sha256={str(p.relative_to(HERE.parent)):sha(p) for p in [
                    HERE.parent/'task-public-flight-2026-10-04/analyze.py',
                    HERE.parent/'task-runtime-2026-09-29/analyze.py']})


if __name__ == '__main__':
    print(json.dumps(generate(Path(sys.argv[1])), indent=1, allow_nan=False))

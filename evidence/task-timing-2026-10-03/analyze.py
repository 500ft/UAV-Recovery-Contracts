"""Summarize the retained attempts. --extract re-reads ULogs with pyulog installed."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def read(run, name):
    path = run / name
    return path.read_bytes() if path.exists() else gzip.decompress((run / (name + '.gz')).read_bytes())


def extract(run):
    from pyulog import ULog
    ulog = ULog(io.BytesIO(read(run, 'flight.ulg')))
    fields = {'failsafe_flags': ['gcs_connection_lost', 'local_position_invalid', 'local_altitude_invalid'],
              'vehicle_status': ['nav_state', 'arming_state', 'gcs_connection_lost'],
              'navigator_status': ['nav_state'],
              'vehicle_local_position': ['xy_valid', 'z_valid'],
              'position_setpoint_triplet': ['current.valid', 'current.type'],
              'sensor_baro': [], 'sensor_mag': [], 'sensor_gps': [],
              'vehicle_global_position_groundtruth': []}
    topics = {}
    for data in ulog.data_list:
        if data.name not in fields:
            continue
        t = [int(v) for v in data.data['timestamp']]
        changes = {}
        for field in fields[data.name]:
            v = data.data[field]
            changes[field] = [dict(t_us=t[i], value=int(v[i])) for i in range(len(t))
                              if i == 0 or v[i] != v[i-1]]
        key = f'{data.name}/{data.multi_id}'
        topics[key] = dict(records=len(t), first_us=t[0], last_us=t[-1],
                           max_adjacent_gap_us=max((b-a for a, b in zip(t, t[1:])), default=None),
                           changes=changes)
        if data.name == 'vehicle_status':
            v = data.data['nav_state']
            topics[key]['mode_changes'] = [dict(first_logged_us=t[i],
                previous_logged_us=t[i-1] if i else None,
                commit_stamp_us=int(data.data['nav_state_timestamp'][i]), nav=int(v[i]))
                for i in range(len(t)) if i == 0 or v[i] != v[i-1]]
    return dict(ulog_sha256=hashlib.sha256(read(run, 'flight.ulg')).hexdigest(),
                dropouts=[dict(timestamp_us=int(d.timestamp), duration_ms=int(d.duration)) for d in ulog.dropouts],
                topics=topics)


def generate():
    runs = {}
    snapshots = {}
    for run in sorted((HERE / 'runs').iterdir()):
        raw = [json.loads(l) for l in read(run, 'raw.jsonl').splitlines()]
        trace = json.loads(read(run, 'trace.json'))
        snapshot = json.loads(read(run, 'parameters-full.json'))
        observation = json.loads(read(run, 'ulog-observations.json'))
        launch = next(r for r in raw if r.get('kind') == 'launch')
        injection = next((r for r in raw if r.get('name') == 'injection'), None)
        overrides = next(r['values'] for r in raw if r.get('kind') == 'param_export')
        params = snapshot['parameters']
        snapshots[run.name] = params
        assert all(params[k]['value'] == v for k, v in overrides.items())
        snapshot_hash = hashlib.sha256(read(run, 'parameters-full.json')).hexdigest()
        assert trace['identity']['execution']['raw_artifacts']['parameters-full.json'] == snapshot_hash
        assert observation['ulog_sha256'] == hashlib.sha256(read(run, 'flight.ulg')).hexdigest()
        timing = {}
        if injection:
            flag_changes = observation['topics']['failsafe_flags/0']['changes']['gcs_connection_lost']
            flag = next(v for v in flag_changes if v['value'] == 1 and v['t_us'] > injection['t_vehicle_s'] * 1e6)
            mode = next(v for v in observation['topics']['vehicle_status/0']['mode_changes']
                        if v['nav'] == 5 and v['commit_stamp_us'] > flag['t_us'])
            navigator = next(v for v in observation['topics']['navigator_status/0']['changes']['nav_state']
                             if v['value'] == 5 and v['t_us'] >= mode['commit_stamp_us'])
            setpoint = next(v for v in observation['topics']['position_setpoint_triplet/0']['changes']['current.valid']
                            if v['value'] == 1 and v['t_us'] >= mode['commit_stamp_us'])
            timing = dict(first_logged_consumed_flag_us=flag['t_us'], rtl_commit_stamp_us=mode['commit_stamp_us'],
                          logged_flag_to_rtl_commit_s=(mode['commit_stamp_us']-flag['t_us'])/1e6,
                          cached_cut_to_rtl_commit_s=mode['commit_stamp_us']/1e6-injection['t_vehicle_s'],
                          last_qualifying_heartbeat_us=None, detector_evaluation_us=None,
                          selected_action_us=None, navigator_execution_bracket_us=None,
                          first_logged_navigator_rtl_us=navigator['t_us'],
                          first_logged_valid_setpoint_after_rtl_us=setpoint['t_us'],
                          commit_to_navigator_status_s=(navigator['t_us']-mode['commit_stamp_us'])/1e6,
                          commit_to_valid_setpoint_s=(setpoint['t_us']-mode['commit_stamp_us'])/1e6,
                          note='logged flag to commit is one segment; cut stamp is a lower bound only; uninstrumented control lacks receive, detector, selector and navigator execution observations')
        runs[run.name] = dict(summary=json.loads(read(run, 'summary.json')),
            binary_sha256=launch['executable_sha256'], instrumentation=launch['build_identity']['instrumentation'],
            clock='one PX4 boot; ULog topic timestamps in hrt_absolute_time microseconds',
            snapshot_sha256=snapshot_hash, snapshot_complete=snapshot['complete'],
            parameter_count=len(params), parameter_types={k:sum(v['type'] == k for v in params.values()) for k in ['INT32','FLOAT']},
            snapshot_host_duration_s=snapshot['host_end_monotonic_s']-snapshot['host_start_monotonic_s'],
            registry_sha256=snapshot['registry_sha256'], injection_cached_vehicle_s=None if injection is None else injection['t_vehicle_s'],
            failures=[r for r in raw if r.get('kind') == 'failure'],
            timing=timing, ulog=observation)
    artifacts = {str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(HERE.rglob('*')) if p.is_file()
                 and p.name not in ['results.json','README.md','checks.json'] and '__pycache__' not in p.parts}
    return dict(evidence_state='executed SIH development attempts; measurement prerequisite blocked',
        attempts=2, completed_injections=1, instrumented_injections=0, confirmation_runs=0,
        full_snapshots=2,
        parameter_value_differences=[k for k in snapshots['dev101']
                                    if snapshots['dev101'][k] != snapshots['original-control'][k]],
        unexecuted_registered_labels=[102,103], timing_pass_fail_enabled=False,
        calibrated_tolerance_s=None, runs=runs, artifact_sha256=artifacts)


if __name__ == '__main__':
    if '--extract' in sys.argv:
        for run in sorted((HERE / 'runs').iterdir()):
            (run / 'ulog-observations.json').write_text(json.dumps(extract(run), indent=1)+'\n')
    print(json.dumps(generate(), indent=1))

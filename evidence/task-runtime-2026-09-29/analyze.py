"""Reproduce results.json from the compressed, executed SITL captures beside it.

Run from any directory with Python's standard library. This reports observations,
not a calibrated injection latency or a whole-study conformance verdict.
"""
import gzip
import hashlib
import json
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent


def read(run, name):
    path = run / name
    if path.exists():
        return path.read_text()
    return gzip.decompress((run / (name + '.gz')).read_bytes()).decode()


def summarize(run):
    raw = [json.loads(line) for line in read(run, 'raw.jsonl').splitlines()]
    trace = json.loads(read(run, 'trace.json'))
    launch = next(r for r in raw if r.get('kind') == 'launch')
    exported = next(r['values'] for r in raw if r.get('kind') == 'param_export')
    injection = next(r for r in raw if r.get('name') == 'injection')
    native, counts = [], {}
    for stage, fields in re.findall(r'UAV_DIAG (\w+) ([^\r\n]*)', read(run, 'px4.log')):
        values = {k: float(v) if '.' in v else int(v)
                  for k, v in re.findall(r'(\w+)=(-?\d+(?:\.\d+)?)', fields)}
        counts[stage] = counts.get(stage, 0) + 1
        if stage != 'init':
            # Lockstep can call Commander twice at the same clock value. Pair
            # the sequential calls, retaining both, rather than keying by time.
            if stage == 'check':
                native.append((values['t'], {}))
            if not native or native[-1][0] != values['t']:
                raise ValueError(f'unmatched {stage} record in {run.name}')
            group = native[-1][1]
            if stage in group:
                raise ValueError(f'duplicate {stage} timestamp in {run.name}')
            group[stage] = {k: v for k, v in values.items() if k != 't'}
    # The first diagnostic used longer lines and was truncated by PX4's log
    # formatter. Only fields actually printed count; no missing value is filled.
    complete = [(t, stages) for t, stages in native
                if all(s in stages for s in ('check', 'params', 'update', 'delay', 'commit'))]
    joint = [(t, s) for t, s in native
             if all(k in s for k in ('check', 'update', 'commit'))]
    active = [(t, s) for t, s in joint if s['check'].get('armed') == 1 and s['check'].get('gcs') == 1]
    effective = sorted({s.get('params', {}).get('dll', s['check'].get('nav_dll_act')) for _, s in active})
    changes, previous = [], None
    for t, s in complete:
        state = dict(armed=s['check']['armed'], gcs=s['check']['gcs'],
                     intended=s['check']['mode'], dll=s['params']['dll'],
                     ignored=s['params']['ignored'], action=s['update']['action'],
                     delayed=s['update']['delayed'], takeover=s['update']['takeover'],
                     deferred=s['update']['deferred'], nav=s['commit']['nav'])
        if state != previous:
            changes.append(dict(t_us=t, **state))
            previous = state
    first_active = active[0][0] if active else None
    first_rtl = next((t for t, s in active if s['update']['action'] == 6), None)
    after = [e for e in trace['events'] if e['name'] == 'native_transition'
             and e['t_vehicle_s'] >= injection['t_vehicle_s']]
    return dict(
        valid=trace['validity'], binary_sha256=launch['executable_sha256'],
        instrumentation=launch['build_identity']['instrumentation'],
        reported_override_readback=exported,
        injection_cached_vehicle_s=injection['t_vehicle_s'],
        injection_timing_scope='lower bound only; no calibrated injection latency',
        native_log_counts=counts, joined_check_update_commit=len(joint),
        complete_native_tuples=len(complete), incomplete_native_tuples=len(native)-len(complete),
        armed_gcs_loss_updates=len(active), effective_nav_dll_act=effective,
        selected_actions_during_armed_gcs_loss=sorted({s['update']['action'] for _, s in active}),
        committed_modes_during_armed_gcs_loss=sorted({s['commit']['nav'] for _, s in active}),
        first_consumed_armed_gcs_loss_us=first_active, first_selected_rtl_us=first_rtl,
        selected_rtl_after_consumed_flag_s=(None if first_active is None or first_rtl is None
                                          else (first_rtl-first_active)/1e6),
        state_changes=changes,
        post_injection_native_mode_events=[dict(t_vehicle_s=e['t_vehicle_s'], **e['detail']) for e in after],
        observation_limit=('first log format truncated: missing fields unknown' if joint and not complete
                           else 'logging can perturb scheduling; this is a development diagnostic'))


def generate():
    runs = {p.name: summarize(p) for p in sorted((HERE / 'runs').iterdir()) if p.is_dir()}
    artifacts = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in sorted(HERE.rglob('*')) if p.is_file()
                 and p.name not in ('results.json', 'README.md') and '__pycache__' not in p.parts}
    return dict(evidence_state='executed SIH SITL development diagnostic', runs=runs,
                artifact_sha256=artifacts,
                limitations=['not a conformance campaign or a symbolic proof',
                             'all integer overrides corrected together; not a single-parameter causal isolation',
                             'native action codes follow framework.h; RTL=6',
                             'historical raw captures and verdicts are preserved unchanged'])


if __name__ == '__main__':
    print(json.dumps(generate(), indent=1))

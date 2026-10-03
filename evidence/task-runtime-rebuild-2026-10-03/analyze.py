"""Reproduce the matched rebuild comparison. --extract re-reads the ULog with pyulog."""
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE = Path(__file__).resolve().parent
PRIOR = HERE.parent / 'task-timing-2026-10-03'


def read(directory, name):
    path = directory / name
    return path.read_bytes() if path.exists() else gzip.decompress((directory / (name+'.gz')).read_bytes())


def generate():
    run = HERE / 'run'
    snapshot = json.loads(read(run, 'parameters-full.json'))
    raw = [json.loads(line) for line in read(run, 'raw.jsonl').splitlines()]
    trace = json.loads(read(run, 'trace.json'))
    launch = next(r for r in raw if r.get('kind') == 'launch')
    registration = json.loads((HERE / 'registration.json').read_text())
    rebuild = json.loads((HERE / 'rebuild.json').read_text())
    assert hashlib.sha256((HERE / 'design.md').read_bytes()).hexdigest() == registration['design_sha256']
    assert launch['executable_sha256'] == rebuild['binary_sha256']
    assert launch['build_identity']['instrumentation'] == 'none'
    for source in rebuild['sources_recompiled']:
        assert ' -c /Users/redhose/.cache/uav-failsafe-composition/px4/PX4-Autopilot/'+source in (HERE/'build.log').read_text()
    observations = json.loads((run/'ulog-observations.json').read_text())
    assert observations['ulog_sha256'] == hashlib.sha256(read(run,'flight.ulg')).hexdigest()
    snapshot_hash = hashlib.sha256(read(run,'parameters-full.json')).hexdigest()
    assert trace['identity']['execution']['raw_artifacts']['parameters-full.json'] == snapshot_hash
    comparisons = {}
    for name in ['dev101','original-control']:
        directory = PRIOR/'runs'/name
        previous = json.loads(read(directory,'parameters-full.json'))
        names = set(snapshot['parameters']) | set(previous['parameters'])
        comparisons[name] = dict(parameter_differences=[k for k in sorted(names)
            if snapshot['parameters'].get(k) != previous['parameters'].get(k)],
            prior_summary_sha256=hashlib.sha256(read(directory,'summary.json')).hexdigest(),
            prior_snapshot_sha256=hashlib.sha256(read(directory,'parameters-full.json')).hexdigest())
    return dict(evidence_state='executed SIH development rebuild control',
        attempts=1, confirmation_runs=0, repair_verification_runs=0,
        new_parameter_count=len(snapshot['parameters']), snapshot_complete=snapshot['complete'],
        snapshot_sha256=snapshot_hash, binary_sha256=launch['executable_sha256'],
        compiled_translation_units=len(rebuild['sources_recompiled']),
        summary=json.loads(read(run,'summary.json')), comparisons=comparisons,
        ulog=observations, additional_timing_observations_executed=False,
        remaining_blocker='The clean rebuild completed. The earlier instrumented failure is not localized to a particular observation call or sensor-work-queue mechanism; no specific repair is isolated.',
        artifacts_sha256={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in ['results.json','README.md','checks.json']
            and '__pycache__' not in p.parts})


if __name__ == '__main__':
    if '--extract' in sys.argv:
        extract = runpy.run_path(str(PRIOR/'analyze.py'))['extract']
        (HERE/'run/ulog-observations.json').write_text(json.dumps(extract(HERE/'run'),indent=1)+'\n')
    print(json.dumps(generate(),indent=1))

"""Print the recorded NP-4 development result from the retained capture."""
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def summarize():
    run = HERE / 'run'
    snapshots = {phase: json.loads((run / f'parameters-{phase}.json').read_text())
                 for phase in ('before', 'after')}
    raw = [json.loads(line) for line in gzip.decompress((run / 'raw.jsonl.gz').read_bytes()).splitlines()]
    trace = json.loads(gzip.decompress((run / 'trace.json.gz').read_bytes()))
    overrides = next(r['values'] for r in raw if r.get('kind') == 'param_export')
    before, after = (snapshots[phase]['parameters'] for phase in ('before', 'after'))
    changes = {name: dict(before=before.get(name), after=after.get(name))
               for name in sorted(set(before) | set(after)) if before.get(name) != after.get(name)}
    hashes = {str(p.relative_to(HERE)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(HERE.rglob('*')) if p.is_file()
              and p.name not in ('results.json', 'README.md') and '__pycache__' not in p.parts}
    return dict(
        purpose='NP-4 development run, excluded from confirmation',
        validity=trace['validity'],
        binary_sha256=trace['identity']['execution']['executable_sha256'],
        snapshots={phase: dict(expected_count=s['expected_count'], captured_count=len(s['parameters']),
                               used_count=s['used_count'], complete=s['complete'], atomic=s['atomic'],
                               elapsed_host_s=s['end_host_monotonic_s']-s['start_host_monotonic_s'])
                   for phase, s in snapshots.items()},
        parameter_changes=changes,
        override_mismatches={phase: {name: dict(override=value, snapshot=s['parameters'].get(name))
                                     for name, value in overrides.items()
                                     if s['parameters'].get(name, {}).get('value') != value}
                             for phase, s in snapshots.items()},
        snapshot_identities=trace['identity']['execution']['parameter_snapshots'],
        mode_transitions=[e['detail'] for e in trace['events'] if e['name'] == 'native_transition'],
        artifact_sha256=hashes)


if __name__ == '__main__':
    print(json.dumps(summarize(), indent=1))

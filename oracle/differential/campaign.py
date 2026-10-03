"""One bounded task-2 corpus. Generate first, then run directed/development/reserved separately.

python oracle/differential/campaign.py generate CONFIG CORPUS
python oracle/differential/campaign.py run CONFIG SEQUENCE_DIR BINARY OUTPUT
Admission is shared by both adapters in this entry point. Direct adapter use is
exploratory and is not covered by this campaign's supported-domain claim.
"""
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import random
import subprocess
import sys

import driver


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def admit(seq, cfg):
    """Task-specific admission, before either adapter sees a sequence."""
    constructed = ran = False
    mode = None
    updates = 0
    try:
        for _, cmd, *args in driver.parse(seq):
            if cmd == 'param' and len(args) == 2:
                assert not constructed, 'parameter after construction'
                allowed = cfg['parameters'].get(args[0], [cfg['fixed_parameters'].get(args[0])])
                assert float(args[1]) in allowed, 'parameter outside declared values'
            elif cmd == 'armed' and len(args) == 1:
                assert args[0] in ('0', '1'), 'armed must be Boolean'
            elif cmd == 'mode' and len(args) == 1:
                assert args[0] in cfg['modes'] and not ran and mode is None, 'mode switching excluded'
                mode = args[0]
                constructed = True
            elif cmd == 'flag' and len(args) == 2:
                assert args[0] in cfg['flags'] and args[1] in ('0', '1'), 'flag outside declared domain'
                constructed = True
            elif cmd == 'run' and len(args) == 2:
                dt = int(args[1])
                seconds = float(args[0])
                assert dt in cfg['tick_ms'] and math.isfinite(seconds) and seconds > 0, 'invalid tick or duration'
                steps = seconds * 1000 / dt
                assert abs(steps - round(steps)) < 1e-8, 'fractional update count'
                updates += round(steps)
                assert updates <= cfg['max_updates'], 'sequence too long'
                constructed = ran = True
            else:
                raise AssertionError('unsupported command or arity')
        assert ran, 'no executed updates'
    except (AssertionError, ValueError) as exc:
        return str(exc)
    return None


def sequence(cfg, seed, stratum):
    r = random.Random(seed)
    params = {k: r.choice(v) for k, v in cfg['parameters'].items()}
    params.update(cfg['fixed_parameters'])
    dt = r.choice(cfg['tick_ms'])
    mode = r.choice(cfg['modes'])
    initial_armed = r.choice([0, 1]) if stratum == 'arming' else 1
    lines = [f'param {k} {v}' for k, v in params.items()] + [f'armed {initial_armed}', f'mode {mode}']
    def run(steps):
        lines.append(f'run {max(1, steps)*dt/1000:.3f} {dt}')
    def flag(name, value):
        lines.append(f'flag {name} {value}')
    a, b = r.sample(cfg['flags'], 2)
    boundary = max(1, math.ceil(params['COM_FAIL_ACT_T'] * 1000 / dt))
    if stratum == 'timer':
        flag(a, 1)
        run(max(1, boundary-1)); run(1); run(1); run(2)
    elif stratum == 'simultaneous':
        flag(a, 1); flag(b, 1); run(1); run(boundary+2)
    elif stratum == 'ordered':
        flag(a, 1); run(r.choice([1, max(1, boundary-1), boundary+1]))
        flag(b, 1); run(boundary+2)
    elif stratum == 'clear_reassert':
        flag(a, 1); run(r.choice([1, max(1, boundary-1), boundary+1]))
        flag(a, 0); run(r.randint(1, 4)); flag(a, 1); run(boundary+2)
    elif stratum == 'arming':
        flag(a, 1); run(r.choice([1, max(1, boundary-1), boundary+1]))
        lines.append('armed 0'); run(r.randint(1, 4))
        if r.choice([False, True]): flag(a, 0); run(1)
        lines.append('armed 1'); run(boundary+2)
    for _ in range(r.randint(*cfg['extra_events'])):
        if stratum == 'arming' and r.random() < .3:
            lines.append(f'armed {r.randrange(2)}')
        else:
            flag(r.choice(cfg['flags']), r.randrange(2))
        run(r.choice([1, 2, max(1, boundary-1), boundary+1]))
    return '\n'.join(lines)+'\n'


def generate(cfg_path, root):
    cfg = json.loads(cfg_path.read_text())
    root.mkdir(parents=True, exist_ok=False)
    manifest = []
    for split in ('development', 'reserved'):
        (root/split).mkdir()
        for si, stratum in enumerate(cfg['strata']):
            for i in range(cfg[split]['per_stratum']):
                seed = cfg[split]['seed']*1000000+si*10000+i
                p = root/split/f'{stratum}-{i:04}.seq'
                p.write_text(sequence(cfg, seed, stratum))
                assert admit(p, cfg) is None, p
                manifest.append(dict(path=str(p.relative_to(root)), seed=seed, stratum=stratum, sha256=digest(p)))
    (root/'directed').mkdir()
    # Boundary cases at each admitted delay, on either side of the threshold.
    for i, delay in enumerate(cfg['parameters']['COM_FAIL_ACT_T']):
        n = max(1, math.ceil(delay*1000))
        p=root/'directed'/f'timer-{i:02}.seq'
        p.write_text(f'param NAV_DLL_ACT 2\nparam COM_FAIL_ACT_T {delay}\nflag gcs_connection_lost 1\nrun {max(1,n-1)/1000:.3f} 1\nrun 0.001 1\nrun 0.001 1\nrun 0.002 1\n')
    for mode in cfg['modes']:
        p=root/'directed'/f'position-{mode}.seq'
        p.write_text(f'param COM_POS_LOW_ACT 3\nparam COM_FAIL_ACT_T 0.5\nmode {mode}\nflag position_accuracy_low 1\nrun 0.1 100\nflag position_accuracy_low 0\nrun 0.1 100\n')
    for name, flags in [('simultaneous',['gcs_connection_lost','geofence_breached']),('reverse',['geofence_breached','gcs_connection_lost'])]:
        for gap in (0, 1):
            p=root/'directed'/f'{name}-{gap}.seq'
            p.write_text('param NAV_DLL_ACT 2\nparam GF_ACTION 5\nparam COM_FAIL_ACT_T 0.2\n'+f'flag {flags[0]} 1\n'+('run 0.01 10\n' if gap else '')+f'flag {flags[1]} 1\nrun 0.3 10\n')
    for i in range(10):
        for stratum in ('clear_reassert','arming'):
            (root/'directed'/f'{stratum}-{i:02}.seq').write_text(sequence(cfg, 7500+i, stratum))
    for p in sorted((root/'directed').glob('*.seq')):
        assert admit(p,cfg) is None
        manifest.append(dict(path=str(p.relative_to(root)), stratum=p.stem.split('-')[0], sha256=digest(p)))
    (root/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print({s:sum(m['path'].startswith(s+'/') for m in manifest) for s in ('directed','development','reserved')})


def run(cfg_path, seqdir, binary, out):
    cfg=json.loads(cfg_path.read_text())
    out.mkdir(parents=True,exist_ok=False)
    results=[]
    for seq in sorted(seqdir.glob('*.seq')):
        row={'sequence':seq.name,'stratum':seq.stem.split('-')[0],'sha256':digest(seq)}
        reason=admit(seq,cfg)
        if reason:
            row.update(status='excluded',reason=reason)
        else:
            dest=out/seq.stem;dest.mkdir()
            with (dest/'native.log').open('w') as log:
                p=subprocess.run([str(binary.resolve())],cwd=dest,env=dict(os.environ,ORACLE_SEQUENCE=str(seq.resolve()),ORACLE_OUT=str((dest/'native.csv').resolve())),stdout=log,stderr=subprocess.STDOUT)
            row['native_exit']=p.returncode
            if p.returncode:
                row.update(status='invalid',reason='native process failed')
            else:
                try:
                    model=driver.run_model(seq)
                    native=driver.read_csv(dest/'native.csv')
                    assert model and native, 'empty output'
                    with (dest/'model.csv').open('w') as f:
                        writer=csv.DictWriter(f,fieldnames=['t_us','action'],lineterminator='\n');writer.writeheader();writer.writerows(model)
                    row.update(status='executed',agree_exactly=model==native,
                               comparison=driver.compare(model,native,driver.dt_of(seq)))
                except (Exception,SystemExit) as exc:
                    row.update(status='invalid',reason=str(exc))
        results.append(row)
        with (out/'results.jsonl').open('a') as f: f.write(json.dumps(row)+'\n')
        if len(results)%100==0: print(len(results),flush=True)
    summary={}
    for group in ['all']+sorted({r['stratum'] for r in results}):
        rr=[r for r in results if group=='all' or r['stratum']==group]
        summary[group]={'attempted':len(rr),'excluded':sum(r['status']=='excluded' for r in rr),'invalid':sum(r['status']=='invalid' for r in rr),'executed':sum(r['status']=='executed' for r in rr),'agree':sum(r.get('agree_exactly',False) for r in rr),'disagree':sum(r['status']=='executed' and not r['agree_exactly'] for r in rr)}
    (out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary))


if __name__=='__main__':
    if sys.argv[1]=='generate': generate(Path(sys.argv[2]),Path(sys.argv[3]))
    elif sys.argv[1]=='run': run(*map(Path,sys.argv[2:]))
    else: raise SystemExit(__doc__)

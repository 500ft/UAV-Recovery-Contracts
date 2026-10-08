"""Render committed result summaries only. No model, native runner or raw-log reads."""
import csv
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/figures'
DOMAIN = ROOT / 'evidence/task-domain-2026-10-03/results.json'
RUNTIME = ROOT / 'evidence/task-observation-qualification-2026-10-04/results.json'
BLUE, RED, GRAY = '#2980b9', '#c0392b', '#606770'
plt.rcParams.update({'font.size': 11, 'axes.titlesize': 12, 'axes.labelsize': 11,
                     'figure.facecolor': 'white', 'axes.facecolor': 'white',
                     'svg.hashsalt': 'retained-results'})


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def finish(fig, name):
    for ext in ('png', 'svg'):
        fig.savefig(OUT / f'{name}.{ext}', dpi=170,
                    metadata={'Date': None} if ext == 'svg' else None)
        if ext == 'svg':
            p = OUT / f'{name}.{ext}'
            p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines()) + '\n')
    plt.close(fig)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    domain = json.loads(DOMAIN.read_text())
    runtime = json.loads(RUNTIME.read_text())
    phases = [('Directed development', [('Before fixes', domain['before']['directed']['all']),
              ('Replayed', domain['development_replay_after_fixes']['directed']['all'])]),
              ('Random development', [('Before fixes', domain['before']['development']['all']),
              ('Replayed', domain['development_replay_after_fixes']['development']['all'])]),
              ('Fresh reserved corpus', [('After fixes', domain['reserved']['all'])])]
    fig, axes = plt.subplots(1, 3, figsize=(11, 4.2))
    fig.subplots_adjust(left=.11, right=.96, bottom=.24, top=.69, wspace=.58)
    table = []
    for ax, (phase, records) in zip(axes, phases):
        for i, (label, r) in enumerate(records):
            assert r['agree'] + r['disagree'] == r['executed']
            ax.barh(i, r['agree'], color=BLUE, height=.43)
            ax.barh(i, r['disagree'], left=r['agree'], color=RED,
                    edgecolor='white', hatch='///', height=.43)
            ax.text(r['executed']/2, i-.32,
                    f"{r['agree']:,} agree / {r['disagree']:,} disagree",
                    ha='center', fontsize=10)
            table.append({'cohort': phase, 'phase': label, **r})
        n = max(r['executed'] for _, r in records)
        ax.set(xlim=(0,n), ylim=(1.7,-.7), yticks=range(len(records)),
               yticklabels=[x for x,_ in records], xlabel='Executed sequences [count]', title=phase)
        ax.set_xticks([0,n/2,n], labels=[f'{x:,.0f}' for x in [0,n/2,n]])
        ax.spines[['top','right']].set_visible(False)
        ax.tick_params(axis='y', length=0, labelsize=10)
    fig.suptitle('Scoped Python / native PX4 comparison', y=.97, fontsize=16)
    fig.text(.5,.865,'Sequence-level counts; development replay and fresh verification shown separately',ha='center',fontsize=11)
    fig.text(.5,.035,'Corpus agreement only. RC loss, mode switching, takeover and integrated behavior excluded.',ha='center',fontsize=10)
    finish(fig,'component-agreement')
    with (OUT/'component-agreement.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=list(table[0]),lineterminator="\n");w.writeheader();w.writerows(table)

    run=runtime['runs']['clean-instrumented']
    timing=run['timing']; segments=timing['native_segments']
    origin=segments['last_observed_qualifying_receive']['t']
    events=[('Last qualifying receive',origin,'receiver marker'),
            ('Last true telemetry publication',segments['publications_matching_detector_anchor'][-1]['t'],'detector anchor'),
            ('First observed aged-false heartbeat',segments['first_observed_aged_false']['t'],'aging marker'),
            ('First false telemetry publication',segments['first_false_telemetry_publication']['t'],'publication marker'),
            ('GCS-loss detector',segments['first_lost_detector_bracket']['t'],'entry/end bracket'),
            ('Consumed GCS-loss input',run['native']['first_consumed_armed_gcs_loss_us'],'class update marker'),
            ('Selected Hold',segments['first_selected_hold']['t'],'selector marker'),
            ('Selected RTL',segments['first_selected_rtl']['t'],'selector marker'),
            ('Committed RTL nav_state',timing['rtl_mode_change']['commit_us'],'ULog nav_state_timestamp'),
            ('Navigator RTL execution',segments['first_navigator_rtl_execution_bracket']['t'],'entry/end bracket')]
    fig, ax=plt.subplots(figsize=(10,5.9))
    fig.subplots_adjust(left=.39,right=.84,top=.77,bottom=.19)
    for i,(name,t,kind) in enumerate(events):
        seconds=(t-origin)/1e6
        ax.plot([0,seconds],[i,i],color='#d9dfe3',lw=1)
        ax.plot(seconds,i,marker='s' if 'bracket' in kind else 'o',color=BLUE,ms=6)
        ax.text(1.04,i,f'{seconds:.3f}',transform=ax.get_yaxis_transform(),va='center',fontsize=11)
    ax.text(1.04,1.06,'Elapsed [s]',transform=ax.transAxes,fontsize=10)
    ax.set(yticks=range(len(events)),yticklabels=[e[0] for e in events],
           ylim=(len(events)-.5,-.5),xlim=(-.4,18),xticks=[0,5,10,15],
           xlabel='Time since last observed qualifying receive [s]')
    ax.axvline(0,color=GRAY,lw=.8)
    ax.tick_params(axis='y',length=0,pad=10)
    ax.spines[['top','right','left']].set_visible(False)
    fig.suptitle('Datalink path on one vehicle clock',x=.06,ha='left',y=.97,fontsize=16)
    fig.text(.06,.895,'Instrumented SIH development run · observed HRT stamps\nCircles: recorded stamps; squares: equal entry/end bracket stamps',fontsize=11,va='top')
    fig.text(.06,.055,'Lockstep quantization does not measure host execution time. Host cut has no upper bound.\nNavigator execution is not actuator response. Timing is descriptive, outside pass/fail.',fontsize=10)
    finish(fig,'datalink-observations')
    with (OUT/'datalink-observations.csv').open('w') as f:
        w=csv.writer(f,lineterminator="\n");w.writerow(['stage','vehicle_hrt_us','since_last_receive_us','observation'])
        w.writerows((name,t,t-origin,kind) for name,t,kind in events)

    lines=['# Retained result tables','',
           'Generated from committed results by `python scripts/plot_retained_results.py`.',
           'These are existing observations. Study A remains paused.','',
           '## Component comparison','',
           '| Cohort / phase | Executed [count] | Agree [count] | Disagree [count] |',
           '| --- | ---: | ---: | ---: |']
    for r in table:
        lines.append('| '+ ' | '.join([r['cohort']+' / '+r['phase']]+[f"{r[k]:,}" for k in ['executed','agree','disagree']])+' |')
    lines += ['', 'Admission counts, with unsupported-input probes kept separate:', '',
              '| Cohort / phase | Attempted [count] | Excluded [count] | Invalid [count] |',
              '| --- | ---: | ---: | ---: |']
    for r in table:
        lines.append('| '+ ' | '.join([r['cohort']+' / '+r['phase']]+[f"{r[k]:,}" for k in ['attempted','excluded','invalid']])+' |')
    probe=domain['admission_probes']
    lines.append(f"| Separate admission probes | {probe['attempted']} | {probe['excluded']} | {probe['invalid']} |")
    lines += ['',f"Separate admission probes: {probe['attempted']} attempted, {probe['excluded']} excluded, {probe['executed']} executed. They are outside the generated cohorts.",
              'Unit: one sequence. Replayed development sequences are reused inputs. The fresh corpus is separate from Study A confirmation.',
              '', '[Source, mechanism breakdown and exclusions](../../evidence/task-domain-2026-10-03/README.md) · [Source JSON](../../evidence/task-domain-2026-10-03/results.json) · [Download CSV](component-agreement.csv)',
              '', '## Instrumented datalink observations','',
              '| Stage | Vehicle HRT [s] | Since last observed receive [s] | Observation |',
              '| --- | ---: | ---: | --- |']
    lines += [f'| {name} | {t/1e6:.3f} | {(t-origin)/1e6:.3f} | {kind} |' for name,t,kind in events]
    lines += ['', 'Decimal display follows this run\'s HRT granularity; it is not an accuracy claim. The detector and navigator brackets have equal entry/end stamps. No host-time duration follows from that equality.',
              '', 'Host-cut upper bound and actuator response: unavailable. Sampled flag brackets, cadence/gaps, binary and typed-parameter identities remain in the source packet.',
              '', '[Source and clock limits](../../evidence/task-observation-qualification-2026-10-04/README.md) · [Source JSON](../../evidence/task-observation-qualification-2026-10-04/results.json) · [Download exact microsecond CSV](datalink-observations.csv)','']
    (OUT/'tables.md').write_text('\n'.join(lines))
    manifest={'generator':'scripts/plot_retained_results.py','command':'python scripts/plot_retained_results.py',
              'matplotlib':matplotlib.__version__,'generator_sha256':digest(Path(__file__)),
              'inputs':{str(p.relative_to(ROOT)):digest(p) for p in [DOMAIN,RUNTIME]},
              'outputs':{p.name:digest(p) for p in sorted(OUT.iterdir()) if p.suffix in ['.png','.svg','.csv','.md']},
              'evidence':'existing component comparisons and instrumented runtime development observations',
              'reference_commit':'bad572fc0902437445a5446bb5bc43098cc6211f'}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')


if __name__ == '__main__':
    main()

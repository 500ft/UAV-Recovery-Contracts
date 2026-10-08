# Data and Figure Contract

## Current state

The [result index](../results/README.md) links committed derived observations
and their external raw archives. Study A confirmation remains incomplete.
The original conceptual diagrams are removed from the working tree. The
[history index](../history/README.md) links their immutable versions. The active summaries below render existing results without new measurements.

## Active figures and tables

| Summary | Input and evidence status | Editable generator / output |
| --- | --- | --- |
| Sequence agreement by phase | Committed [component counts](../evidence/task-domain-2026-10-03/results.json); declared-domain comparison | [Generator](../scripts/plot_retained_results.py), [PNG](../results/figures/component-agreement.png), [SVG](../results/figures/component-agreement.svg) |
| Datalink event observations | Committed [runtime result](../evidence/task-observation-qualification-2026-10-04/results.json); one instrumented SIH development run | Same generator, [PNG](../results/figures/datalink-observations.png), [SVG](../results/figures/datalink-observations.svg) |
| Accessible result tables | Derived views of those same JSON records, with integer counts and clock units | [Markdown and CSV links](../results/figures/tables.md) |

Use an environment with Matplotlib (the rendered version is in the
[manifest](../results/figures/manifest.json)):

```sh
python scripts/plot_retained_results.py
```

The generator only reads committed aggregate results. It writes figures,
downloadable tables and input/output hashes. It does not execute the model,
autopilot, raw-log extraction or reserved cases. Repository validation still
uses the existing dependency set; Matplotlib is only needed to redraw figures.

The visual reference is the owner's enclosure [bias generator](https://github.com/500ft/sensor-enclosure-thermal-design/blob/bad572fc0902437445a5446bb5bc43098cc6211f/analysis/thermal_bias.py)
and its rendered bias/transient figures at that commit. White panels, explicit
units, restrained grids and marker/hatch redundancy carry over. Different
component sample counts use explicitly labeled axes; runtime events use a
single clock. Neither summary invents uncertainty bands.

## Inventory and retained material

The public repository had no scientific PNG/SVG plots after cleanup. The
README's long result table is now a compact boundary table plus the component
figure; the active result index adds the runtime view. Archived evidence tables
remain unchanged because they record original execution and exclusions. The
public-log observation stays a linked table: incomplete histories and an older
firmware revision prevent an admitted comparison. No result from it is combined
with the SIH clock. The historical dependency map remains a source-audit diagram,
not a quantitative result, and is unchanged.

The separate local successor has an existing core-qualification plot and its
own generator/manifest. Its local restyling is not published in this repository.
The scientific roadmap and pending decisions are unchanged.

## Planned data stages

```text
data/raw/<study>/<configured-vehicle>/<run-id>/
data/processed/<study>/<analysis-version>/
results/generated/<study>/<analysis-version>/
```

Raw logs remain immutable. Processed data record the source run IDs, processing commit, environment, and command. Large binary flight logs are stored in a versioned external archive rather than committed directly.

## Required trace metadata

- Study and run identifiers
- Evidence state: simulation, HITL, or measured
- Autopilot and firmware identifier
- Complete configuration hash
- Airframe identity and dynamics model
- Test environment and random seed
- Recovery intention and authority-loss event
- Initial condition and terminal condition
- Logging clock, sampling rate, units, and coordinate frame
- Software commit that produced processed output

## Figure rules

Every future figure must state:

1. The claim it supports
2. Evidence state
3. Conditions and sample unit
4. Input artifacts
5. Generator command and commit
6. Uncertainty representation
7. Output path

Color is never the only semantic channel. Measured or held-out traces use solid lines with markers; model or calibration traces use dashed lines; thresholds are directly labeled.

## Historical figure manifest

| ID | Artifact | Claim | Evidence state |
| --- | --- | --- | --- |
| URC-00 | [`assets/recovery-contracts-overview.svg`](https://github.com/500ft/uav-failsafe-composition/blob/cdb7b36d01085527529fde3bead4543c1e038e43/assets/recovery-contracts-overview.svg) | Explains the proposed method only | Planned / conceptual |
| URC-AUDIT-01 | [`docs/research-dependency-audit.md`](research-dependency-audit.md#directed-dependency-map) | Explains the source-reviewed task and gate order | Planned / source-reviewed |

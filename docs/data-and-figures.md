# Data and Figure Contract

## Current state

The [result index](../results/README.md) links committed derived observations
and their external raw archives. Study A confirmation remains incomplete.
The original conceptual diagrams are removed from the working tree. The
[history index](../history/README.md) links their immutable versions. This
reconciliation creates no new failsafe figure or measurement.

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

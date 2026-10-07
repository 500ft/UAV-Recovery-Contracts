# Research Plan

Historical study material. Active questions are superseded by the software
pivot; Study A is paused. See the [history index](../history/README.md) for
disposition and the retained evidence. This text does not authorize new runs.

## Position

The broad topics—UAV failsafes, contingency trajectories, collision avoidance, safety contracts, and health-aware task allocation—are established. This project does not claim those ideas as new.

The candidate contribution is narrower: measure the native post-authority-loss behavior of a **completely configured vehicle**, form an empirical recovery contract from those observations, and test whether multiple such contracts can be composed more efficiently than one fleet-wide worst-case envelope.

## 2026-09-16 position note

The [formal-composition programme](specs/formal-composition/README.md) is the proposed spine: extract PX4's failsafe logic as a timed-automaton network, decide safety, deadlock freedom, priority consistency and bounded time-to-safe-state on the composed model, and replay every witness in SITL. RQ1–RQ2 below become its measurement layer and fallback; RQ3–RQ4 are trigger-gated (see its scope). The unit of analysis, observables and honesty rules below are unchanged.

## Unit of analysis

Each experimental identity is:

> autopilot + firmware commit or release + airframe model + complete parameter file + recovery intention

“PX4” and “ArduPilot” are not treatments by themselves. A brand-level conclusion would hide configuration, tuning, and version effects.

## Research questions

### RQ1 — Configuration sensitivity

How much do authority-transition latency, mode sequence, braking response, and recovery trajectory vary across configured-vehicle identities that are intended to perform equivalent Hold, Land, or RTL behavior?

### RQ2 — Contract calibration

Can a recovery tube calibrated on one trace set achieve its target coverage on held-out runs from the same configured identity?

### RQ3 — Value of individualization

At matched held-out coverage, how much integrated space-time volume is saved by configuration-specific tubes relative to one global worst-case tube?

### RQ4 — Fleet composition

When a vehicle loses offboard authority, does reserving its calibrated tube and evacuating cooperative neighbors reduce conflicts at lower mission cost than reserving the global envelope?

## Falsifiable hypotheses

- **H1:** At least one measured authority-transition or trajectory statistic differs across equivalently intended configurations by more than run-to-run uncertainty.
- **H2:** Configuration-specific recovery tubes retain their registered held-out coverage.
- **H3:** Configuration-specific tubes use less integrated reserved volume than a fleet-wide tube at matched coverage.
- **H4:** Neighbor evacuation around a held-out native recovery trace reduces conflict exposure without falling back to fleet-wide weakest-capability operation.

Any hypothesis may fail and remains reportable.

## Primary observables

- Time from final valid setpoint to native mode transition
- Time from transition to settled Hold, Land, or RTL behavior
- Mode and command-authority sequence
- Position, velocity, attitude, altitude, and battery state
- Reconnection acceptance or rejection sequence
- Minimum observed separation in composed encounters
- Recovery-tube coverage on held-out traces

## Primary estimands

### Held-out tube coverage

The fraction of held-out trajectories fully contained by the registered tube over the registered horizon. Coverage is reported with uncertainty; a nominal percentage alone is insufficient.

### Integrated reserved volume

For a position tube \(T(t)\), the comparison quantity is:

\[
V_4 = \int_0^H \operatorname{Vol}(T(t))\,dt.
\]

The horizon, coordinate frame, sampling interval, and numerical integration rule must be fixed before the final comparison.

### Mission cost

A paired difference in completed weighted task value per minute under the same encounter and failure trace. The task generator and weights must be frozen before confirmatory evaluation.

## Minimum comparison set

1. Native configured failsafe with no fleet coordination
2. One fleet-wide worst-case recovery tube
3. Configuration-specific empirical recovery tubes
4. Configuration-specific tubes with cooperative-neighbor evacuation
5. Oracle using the realized future trajectory, reported only as an upper bound

Time scaling, barrier filtering, health-aware task allocation, and joint mission/recovery optimization are extensions, not minimum requirements.

## Analysis principles

- Primary calibration/confirmation split: independent run groups within each pinned configured identity. Adjacent time samples are not independent observations. Entirely unseen configured identities are a separate transfer study, not interchangeable with this split.
- Calibrate tubes without access to held-out traces.
- Report effect sizes and uncertainty, not only hypothesis-test outcomes.
- Separate physical demonstrations from statistical safety claims.
- The global envelope is a fallback only within its own established domain. Outside both domains, abstain from empirical safety claims; specify any operational response under a separately approved safety procedure.
- Freeze final thresholds only after a pilot estimates variability; pilot data cannot enter the confirmatory test set.

### Fleet-claim gate (prospective; not satisfied)

Single-vehicle trajectory coverage is not fleet-level safety. Before RQ4 can
support a fleet claim, define the mission horizon, fleet safety event, allowable
joint failure probability, per-contract risk allocation, separation margin, and
neighbor command-authority assumptions. Account for common-mode communication,
navigation and environmental failures. Ten independent 95%-coverage events all
hold with probability only `0.95**10 ≈ 0.599`; independence is not assumed here.
Without independence, use a justified joint model or a conservative risk bound,
not multiplication of individual coverage values. Encounter evaluations must
include failures that affect cooperative neighbors together.

This design amendment narrows future claims. No risk allocation, trajectory
coverage or operational safety guarantee has been measured or established.

## Scope

### In the minimum publishable core

- PX4 and ArduPilot SITL
- Exact configuration manifests
- Offboard-stream and companion-process termination
- Hold, Land, and RTL intentions
- Empirical trace and tube benchmark
- Held-out conformance and volume comparison

### Outside the minimum core

- Large physical swarm
- Universal autopilot ranking
- Formal safety proof for unmodeled environments
- GPS-denied navigation failures
- Adversarial security claims
- Joint task allocation and recovery optimization

## Honest outcomes

- **Positive:** individual contracts retain coverage and materially reduce reservation cost.
- **Null:** the global tube is nearly as efficient; individualization is unnecessary in the tested envelope.
- **Conformance failure:** native behaviors are too variable for the proposed tube model.
- **Tooling contribution:** release the pinned cross-stack trace benchmark and configuration schema even if fleet composition is not justified.

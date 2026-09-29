# Traceability index

One row per consequential decision: what it answers, where its reasoning lives, which registered quantities it
consumes, what has validated it, and its status. **The reasoning is not duplicated here.** Follow the link.

Quantity ids resolve in [`protocols/quantities.json`](../protocols/quantities.json). Provenance and evidence
status are defined there, and [`docs/number-provenance-audit-2026-09-25.md`](number-provenance-audit-2026-09-25.md)
is the audit that produced it.

## Apparatus and measurement

| decision | reasoning lives in | consumes | validation | status |
|---|---|---|---|---|
| A timing instant's bound is open above | [event-semantics §7](../protocols/event-semantics.md) | — | `TimeBoundTests`, the delayed-telemetry counterexample | **settled**; D16 corrected |
| The injection instant is a cached stamp | [event-semantics §7](../protocols/event-semantics.md) | — | `test_the_injection_instant_is_a_cached_stamp_with_an_open_upper_side` | **settled**; D23 |
| No timing verdict here can pass | [event-semantics §7](../protocols/event-semantics.md) | `Q-RESIDUAL` | every historical latency re-derives as inconclusive | **settled**; D24 |
| Development tolerance stays 1.5 s | [expected-timelines tolerance](../protocols/expected-timelines.json) | `Q-TOL`, `Q-REPEAT-OLD` | none possible from these runs | **frozen, unvalidated**; D20 |
| A statistic needs a cohort | [reproducibility docstring](../harness/reproducibility.py) | `Q-COHORT-MIN` | `ReproducibilityCohortTests`, all three owner probes | **settled**; D21 |
| Flag values stay native, coverage stays separate | [event-semantics §7](../protocols/event-semantics.md) | — | `ObservationSemanticsTests`, four fixtures | **settled** |
| A run is invalid after a 2 s heartbeat gap | [trace.py validity](../harness/trace.py) | `Q-HB-GAP`, `Q-HB-RATE` | caught the 2026-09-20 rep1 crash | **settled** |

## Identity

| decision | reasoning lives in | consumes | validation | status |
|---|---|---|---|---|
| Scenario, execution and analysis are three identities | [identity.py](../harness/identity.py) | `Q-HORIZON`, `Q-INJECT-T`, `Q-SEED-OFFSETS` | `tests/test_identity.py`, 13 cases | **settled**; D25 |
| The parameter readback is not a configuration | [identity.py](../harness/identity.py) | — | `test_the_parameter_readback_is_never_called_complete` | **settled**; a complete snapshot needs a new run |
| Legacy captures key on id plus content hash | [legacy-captures.json](../evidence/task-measurement-repair-2026-09-24/legacy-captures.json) | — | all 10 captures, 2 ambiguous ids reported | **settled** |

## Properties and obligations

| decision | reasoning lives in | consumes | validation | status |
|---|---|---|---|---|
| U1, response obligation | [properties U1](../protocols/unsafe-composition-properties.json) | `Q-DL-LOSS-T`, `Q-FAIL-ACT-T`, `Q-RESIDUAL` | mode and action parts evaluable; timing not | **partial** |
| U2, arbitration | [properties U2](../protocols/unsafe-composition-properties.json) | `Q-FAIL-ACT-T`, `Q-RECHARGE` | model fixtures only | **unobservable in SITL** |
| U3, oscillation | [properties U3](../protocols/unsafe-composition-properties.json) | `Q-U3-WINDOW`, `Q-RECHARGE` | six shared-delay fixtures | **specified**; query Q4 added |
| U4, response commitment | [properties U4](../protocols/unsafe-composition-properties.json) | `Q-U4-MARGIN`, `Q-RESIDUAL` | mode commitment evaluable | **partial**; D17 split completion out |
| Physical completion is out of scope | [properties U4 model_boundary](../protocols/unsafe-composition-properties.json) | — | none needed; the old bound was a lower bound used as a deadline | **settled**; D17 |
| Coverage gate replaces the pooled binomial gate | [decisions D7](specs/formal-composition/decisions-2026-09-19.md) | `Q-WILSON` | arithmetic verified | **settled** |

## Model correspondence

| decision | reasoning lives in | consumes | validation | status |
|---|---|---|---|---|
| The delay pot is shared and recharges at a quarter rate | [px4_failsafe.py](../model/px4_failsafe.py) | `Q-RECHARGE`, `Q-FAIL-ACT-T` | [11 sequences, model vs the real class, exact](../evidence/task-differential-2026-09-29/README.md); `tests/test_differential.py` | **differentially checked** on the action timeline; D27, D28 |
| No delay below 0.1 s | [px4_failsafe.py](../model/px4_failsafe.py) | `Q-DELAY-EPS` | s8 and s9 probe both sides in the real class | **differentially checked**; the exact boundary is not probed |
| The native class is the differential oracle | [oracle script](../oracle/run_native_failsafe_test.sh) | `Q-ORACLE-BUDGET` | [run 36222455516](../evidence/task-oracle-2026-09-26/README.md): 9/9 cases pass, binary hashed | **environment closed**; D14. The differential itself has not been run: D26 |

## Literature identity

| decision | reasoning lives in | consumes | validation | status |
|---|---|---|---|---|
| Identity is separate from access | [register identity_vocabulary](../literature/register.json) | — | `tests/test_literature_register.py` | **settled** |
| A title check cannot catch a wrong-work match | [fixture](../tests/fixtures/literature-l32-mismatch.json) | `Q-TITLE-SIM` | L32 scored a clean match on the wrong work | **settled** |
| Every row carries an intent disposition | [register](../literature/register.json) | — | 55 of 55 dispositioned; 4 unresolved | **settled**; no paper marked read |

## Open, with the next action

| what is open | blocks | next action |
|---|---|---|
| `Q-RESIDUAL` has no bound | every timing verdict in this apparatus | a transport or timebase bound, or a causally post-event acknowledgment |
| The selector agrees with the model but the anomaly is unexplained | Study A | instrument the running autopilot at `FailsafeBase::update` (layer C); the selector itself is now the least likely location |
| The detector runs 1.4 to 2.0 s late against its documented timeout | T1, T2 and T5 | the oracle, then the runtime instrumentation |
| No recovery action has ever been observed | Study A | layers A and B compared first, then the runtime instrumentation for layer C |

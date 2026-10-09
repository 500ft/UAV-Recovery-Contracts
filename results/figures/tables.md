# Retained result tables

Generated from committed results by `python scripts/plot_retained_results.py`.
These are existing observations. Study A remains paused.

## Component comparison

| Cohort / phase | Executed [count] | Agree [count] | Disagree [count] |
| --- | ---: | ---: | ---: |
| Directed development / Before fixes | 36 | 25 | 11 |
| Directed development / Replayed | 36 | 36 | 0 |
| Random development / Before fixes | 1,500 | 1,005 | 495 |
| Random development / Replayed | 1,500 | 1,500 | 0 |
| Fresh reserved corpus / After fixes | 1,000 | 1,000 | 0 |

Admission counts, with unsupported-input probes kept separate:

| Cohort / phase | Attempted [count] | Excluded [count] | Invalid [count] |
| --- | ---: | ---: | ---: |
| Directed development / Before fixes | 36 | 0 | 0 |
| Directed development / Replayed | 36 | 0 | 0 |
| Random development / Before fixes | 1,500 | 0 | 0 |
| Random development / Replayed | 1,500 | 0 | 0 |
| Fresh reserved corpus / After fixes | 1,000 | 0 | 0 |
| Separate admission probes | 8 | 8 | 0 |

Separate admission probes: 8 attempted, 8 excluded, 0 executed. They are outside the generated cohorts.
Unit: one sequence. Replayed development sequences are reused inputs. The fresh corpus is separate from Study A confirmation.

[Source, mechanism breakdown and exclusions](../../evidence/task-domain-2026-10-03/README.md) · [Source JSON](../../evidence/task-domain-2026-10-03/results.json) · [Download CSV](component-agreement.csv)

## Instrumented datalink observations

| Stage | Vehicle HRT [s] | Since last observed receive [s] | Observation |
| --- | ---: | ---: | --- |
| Last qualifying receive | 57.872 | 0.000 | receiver marker |
| Last true telemetry publication | 60.132 | 2.260 | detector anchor |
| First observed aged-false heartbeat | 60.384 | 2.512 | aging marker |
| First false telemetry publication | 60.388 | 2.516 | publication marker |
| GCS-loss detector | 70.140 | 12.268 | entry/end bracket |
| Consumed GCS-loss input | 70.152 | 12.280 | class update marker |
| Selected Hold | 70.152 | 12.280 | selector marker |
| Selected RTL | 75.156 | 17.284 | selector marker |
| Committed RTL nav_state | 75.156 | 17.284 | ULog nav_state_timestamp |
| Navigator RTL execution | 75.156 | 17.284 | entry/end bracket |

Decimal display follows this run's HRT granularity; it is not an accuracy claim. The detector and navigator brackets have equal entry/end stamps. No host-time duration follows from that equality.

Host-cut upper bound and actuator response: unavailable. Sampled flag brackets, cadence/gaps, binary and typed-parameter identities remain in the source packet.

[Source and clock limits](../../evidence/task-observation-qualification-2026-10-04/README.md) · [Source JSON](../../evidence/task-observation-qualification-2026-10-04/results.json) · [Download exact microsecond CSV](datalink-observations.csv)

# Fresh builds recover the instrumented datalink trace

Both members of the matched development pair completed datalink loss and RTL.
Their full typed parameter values and observed mode-transition sequences match.
The fresh instrumented build did not reproduce the earlier tracking failure.
[results.json](results.json) holds the run counts, parameter comparison,
topic gaps, native records, clock segments and raw-file hashes.

Study A confirmation did not start. The current model and adapters still lack
required GPS/estimator-validity behavior, and the existing campaign helper does
not enumerate every applicable configuration row. Those are repairable
development prerequisites, not a model-structure kill under D7.

## What was executed

The [design](design.md) and [registration](registration.json) were committed
before either build or run. The [control build](build-control.json) and
[instrumented build](build-instrumented.json) were recorded in separate commits
before their launches. Both start from empty build directories, use the pinned
source and installed compiler, target `px4`, retain the compiler warnings and
disable compiler caching. The [build comparison](build-comparison.json) finds
identical compile commands after replacing only the build-directory prefix.
Full verbose logs and build metadata remain in the external cache.

The prior [cache-disabled control](../task-runtime-rebuild-2026-10-03/README.md)
recompiled selected uninstrumented files. It did not perform a fresh
instrumented build. This pair fills that gap using the unchanged
[observation patch](../task-timing-2026-10-03/instrumentation.patch), the same
scenario, explicit development offset and full typed pre-arm snapshot. Each
member uses a fresh process and working directory. Confirmation seeds were
not used.

Both runs reached normal tracking before injection. Barometer, magnetometer
and GPS samples continued through the logged flight. The log closes after
disarm, before the runner finishes its observation horizon; its endpoint is
not evidence of the earlier airborne sensor interruption. No ULog dropout
records were reported. The instrumented console supplied complete joined
check/parameter/update/delay/nav-assignment tuples, with repeated HRT values
retained as separate calls. That tuple covers the fields printed by the patch,
not every input to the native class.

The two successful runs do not identify the old failure's cause. Freshly
rebuilding all objects changes more than compiler-cache reuse, and a single
pair cannot rule out intermittent scheduling effects. No PX4 behavior was
changed and no specific cache or logging repair is claimed. Historical failed
attempts and saved binaries remain intact. [Restoration](restoration.json)
confirms clean pinned source and unchanged original binary hashes.

## One event, separate clocks and stages

The instrumented run's last observed qualifying receive precedes selected RTL
by 17.284 seconds on its vehicle HRT clock. That is a descriptive receive-to-
selection interval. The host cut uses another clock and retains only an
open-above vehicle-clock bound. The following fields in `results.json` allow
the complete observed path to be inspected without substituting one timestamp
for another:

| Stage | Record and meaning |
|---|---|
| Host injection | `timing.host_injection_elapsed_s` and `cached_vehicle_injection_interval_us`; the cached stamp is a lower bound, not the last receive |
| Qualifying receive | `native_segments.last_observed_qualifying_receive`; captured in the receiver's GCS-heartbeat branch |
| Aging and telemetry | `first_observed_aged_false`, `publications_matching_detector_anchor` and `first_false_telemetry_publication`; the last true publication advances commander's anchor after the last receive |
| Detector | `first_lost_detector_bracket`; entry/end HRT reads surround the timeout check |
| Consumed input | `native.first_consumed_armed_gcs_loss_us`; the printed GCS flag at an actual class update, distinct from its earlier ULog publication |
| Selected action | `first_selected_hold` and `first_selected_rtl`; records after class selection, with the update-time argument retained |
| Committed mode | `timing.rtl_mode_change.commit_us` comes from `nav_state_timestamp`. The patch's `UAV_TIME commit` marker follows nav-field assignment but precedes assignment of that official stamp |
| Navigator | `first_navigator_rtl_execution_bracket` surrounds mode execution and setpoint publication. `navigator_rtl` is a separate logged status report. Neither measures actuator response or recovery completion |

See the existing [pinned source trace](../task-timing-2026-10-03/README.md#source-trace-and-observable-intervals-np-3)
for the receiver, detector, selection and navigator paths. Equal entry/end HRT
values are consistent with SIH lockstep clock resolution; they do not prove
zero execution time. Adjacent sample gaps describe this run and provide no
hard upper bound on scheduling delay. The sampled false/true flag bracket
is wider than the actual printed consumed-input observation. No historical
tolerance was changed or newly calibrated.

## Logger qualification and remaining gates

At the pin, [default subscriptions](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/logged_topics.cpp#L48)
already request `failsafe_flags` and `vehicle_status` without topic throttling;
telemetry has its own interval. The [health-check publisher](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/HealthAndArmingChecks/HealthAndArmingChecks.cpp#L106)
publishes on changed results or its periodic condition, so a maximum-rate
subscription cannot recover every consumed selector input. Actual sample
counts, gaps and channel instances are recorded separately for each run.

The logged CPU and RAM fields are zero because the pinned
[LoadMon implementation](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/load_mon/LoadMon.cpp#L165)
has no Darwin calculation branch. They cannot bound instrumentation overhead.
Dropout records and topic gaps also do not measure every console/uORB queue
wait or blocked callback. Tracking completed with each logging setup, but this
pair establishes no timing-equivalence or CPU-overhead bound. A logger-only
alternative was unnecessary after the instrumented run succeeded, and would
not supply unpublished internal inputs.

[Protocol section 7b](../../docs/specs/formal-composition/study-a-protocol.md#7b-amendment-2026-09-30--success-criterion-after-the-decision-sign-off)
permits discrete agreement to decide while timing remains non-gating. It still
requires a valid, observable, classified result for every required cell.
The [executed prerequisite inspection](prerequisite-inspection.json) records:

- `configured_action('gps_loss', DEFAULTS)` raises `KeyError`. The
  [native fallback path](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/failsafe/failsafe.cpp#L659)
  depends on validity and mode requirements. Substituting the distinct
  position-accuracy mechanism would change the experiment.
- The native differential adapter cannot accept offboard-loss, battery-warning
  or estimator-validity inputs. Its existing admitted corpus remains narrower
  than the integrated campaign. The runtime patch likewise prints only some
  consumed flags and no complete consumed takeover-request vector.
- `single_event_campaign()` selects only the RTL and Hold rows. It cannot be
  used unchanged as the signed all-applicable-row D25 list. The current
  hand-timeline verifier also combines timing and window verdicts; it is not
  a frozen full-matrix discrete-only model comparison.

The missing state exists in PX4 and can be added and checked in development.
This task stops at those prerequisites rather than selecting a reduced
confirmation matrix. D25 and the confirmation freeze remain uncommitted.
Public-log replay stays separately excluded. The next development step is to
qualify the remaining mechanism inputs and comparison, then freeze the full
required cells before confirmation.

## Reproduce

Raw captures and full build logs stay in the external directory indexed by
[external-artifacts.json](external-artifacts.json). With the existing pyulog
environment and that directory assigned to `UAV_QUALIFICATION_CACHE`:

```sh
python evidence/task-observation-qualification-2026-10-04/analyze.py "$UAV_QUALIFICATION_CACHE" > /tmp/uav-qualification-results.json
cmp /tmp/uav-qualification-results.json evidence/task-observation-qualification-2026-10-04/results.json
python -m unittest discover -s tests -p test_observation_qualification.py
```

[checks.json](checks.json) records local validation. The extraction was repeated
from the unchanged raw cache and matched byte for byte. The existing domain
audit reads the retained campaign record; it does not rerun that native corpus.
The initial build-command comparison omitted normalization of generated-file
keys. Its spurious differences remain in the external cache, and the corrected
comparison changes no source, binary or run. No firmware/model repair iteration
was performed during this pair.

The owner's exercise is to reproduce the instrumented receive-to-RTL path,
explain why the timeout anchor is later than the receive, and distinguish the
sampled flag bracket from consumed input, mode commit and navigator execution.
Explain why none of these observations closes the host injection's upper bound.

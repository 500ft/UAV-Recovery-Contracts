# Roadmap

This is the plan for finishing the project. The long-term backlog is
[docs/TASKS.md](docs/TASKS.md); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The project is finished when **Study A** has run: the required single-event
SITL cells on pinned PX4 v1.17.0, each compared with the prediction from the
Python model of PX4's failsafe logic, and judged by the coverage gate in
[decision D7](docs/specs/formal-composition/decisions-2026-09-19.md) (as
revised on 2026-09-25, signed off 2026-09-30):

- every required cell has a valid, observable, classified result, reported by
  mechanism, order and boundary;
- any unexplained discrepancy blocks claims for its subdomain;
- a disagreement that is a model-structure error, and can't be fixed without
  adding state the pinned code doesn't contain, ends the formal model.

The required cells are at least the five injectable event classes on each
configuration where the class has a configured action, at seeds 1, 2, 3, 5
and 8 ([protocol §7b](docs/specs/formal-composition/study-a-protocol.md)).
Every outcome ends in a release: pinned configurations, injection harness,
traces, and the comparison against the model. A result where the model fails
still finishes the project.

This is PX4 only. ArduPilot was dropped on 2026-09-24 because PX4's own
behaviour was not yet explained ([critique](docs/specs/formal-composition/critique-2026-09-24.md)).

## Where it stands

- **The reserved corpus agrees after the scoped model repairs.** Directed and
  random development found eligibility, clearing and shared-delay registration
  errors. Their counterexamples are preserved. The implementation was frozen
  before fresh verification, with results reported by mechanism and sequence
  ([results](evidence/task-domain-2026-10-03/results.json)). The earlier POSCTL
  position-accuracy discrepancy is resolved on its recorded trace. Under D7,
  claims remain limited to the [declared domain and executed corpus](evidence/task-domain-2026-10-03/README.md):
  fixed modes and the admitted datalink, geofence and position flags. RC loss,
  mode switching, takeover and integrated vehicle behavior remain excluded.
- **SITL runs now produce failsafes.** From 2026-09-21 to 09-29 every SITL run
  showed no failsafe action at all. The cause was the harness: it sent integer
  PX4 parameters as floats, so PX4 read a garbage action setting and chose
  "none". With the encoding fixed, a datalink loss in Auto Loiter gives Hold,
  then RTL, including on the unmodified PX4 binary
  ([evidence](evidence/task-runtime-2026-09-29/README.md)).
- **Full typed parameter capture now runs (NP-4).** The new instrumented
  executable failed tracking before injection; the original-executable control
  completed datalink loss with identical pre-arm parameter values. Both attempts
  are [retained](evidence/task-timing-2026-10-03/README.md). The source trace
  identifies heartbeat aging and telemetry publication before commander's
  configured timeout. Full-chain measurement is blocked on diagnosing the
  instrumented runtime's tracking failure. NP-6 sets no replacement tolerance:
  host stream cessation still has no vehicle-clock upper bound, so timing remains
  outside pass/fail under the signed protocol.
- RC loss can't be injected in this simulator setup (decision D13), so Study A
  covers the other event classes.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Sign off decisions D1–D13 | Owner | Done 2026-09-30 ([addendum](docs/specs/formal-composition/decisions-2026-09-19.md)) |
| 2 | Reproduce and fix armed-state handling against the pinned native class | Agent | Done for the exercised cases; [evidence](evidence/task-armed-2026-10-03/README.md) |
| 3 | Define the supported domain, resolve the recorded mode counterexample, then run directed and stratified random cases with reserved verification | Agent | Done for the [executed corpus](evidence/task-domain-2026-10-03/README.md); no universal equivalence claim |
| 4 | Close NP-3, NP-4 and NP-6; separate observable timing segments on one vehicle clock | Agent | NP-4 executed. NP-3 source traced; runtime segmentation blocked by the retained tracking failure. NP-6 remains uncalibrated. **Next:** diagnose the instrumented runtime before further measurement or confirmation |
| 5 | Commit the required cell list as scenario identities (D25), then run every cell and compare each with the model | Agent | Traces committed; every cell classified |
| 6 | Apply the D7 gate. If the model holds, run the first supported hazard pair (D9) | Agent | Gate result and any blocked subdomains recorded |
| 7 | Release the benchmark: configurations, harness, traces, model, comparison report | Agent | Tagged release with a README that states the verdict |

The model checker (UPPAAL) is deferred under D8 option (b): it is only needed
for composition properties beyond Study A.

## Not in this version

- ArduPilot or any second autopilot.
- HITL, flight tests and multi-vehicle work. These need hardware, a facility
  and a safety owner (TASKS.md tier 2).
- The per-configuration recovery-envelope comparison from the original plan.
  It can follow a passing Study A.

# Roadmap

This is the plan for finishing the project. The long-term backlog is
[docs/TASKS.md](docs/TASKS.md); work history is in
[docs/SPRINT_PROGRESS.md](docs/SPRINT_PROGRESS.md) and
[docs/REVIEW_READY.md](docs/REVIEW_READY.md).

## Finish line

The project is finished when **Study A** has run: 60 single-event SITL cases
on pinned PX4 v1.17.0, each compared with the prediction from the Python model
of PX4's failsafe logic, and judged by the registered agreement rule
([decision D7](docs/specs/formal-composition/decisions-2026-09-19.md)):

- 3 or fewer disagreements: the model is a usable predictor. Release it with
  the benchmark.
- 4 to 6: every disagreement is root-caused, and the owner decides.
- 7 or more: drop the formal model and release the benchmark on its own.

Every branch ends in a release: pinned configurations, injection harness,
traces, and the comparison against the model. A result where the model fails
still finishes the project.

This is PX4 only. ArduPilot was dropped on 2026-09-24 because PX4's own
behaviour was not yet explained ([critique](docs/specs/formal-composition/critique-2026-09-24.md)).

## Where it stands (2026-09-30)

- **The model matches PX4's real failsafe class.** On 11 input sequences the
  Python model and PX4's compiled `Failsafe` class agree update for update. The
  first comparison exposed an ordering bug in the model, which was fixed
  ([evidence](evidence/task-differential-2026-09-29/README.md)).
- **SITL runs now produce failsafes.** From 2026-09-21 to 09-29 every SITL run
  showed no failsafe action at all. The cause was the harness: it sent integer
  PX4 parameters as floats, so PX4 read a garbage action setting and chose
  "none". With the encoding fixed, a datalink loss in Auto Loiter gives Hold,
  then RTL, including on the unmodified PX4 binary
  ([evidence](evidence/task-runtime-2026-09-29/README.md)).
- The RTL arrives 16.4–16.7 s after the link is cut. The configured timers
  account for 15 s (10 s detection, 5 s hold). The extra time is open item NP-3.
- RC loss can't be injected in this simulator setup (decision D13), so Study A
  covers the other event classes.

## What's left

| # | Step | Who | Done when |
|---|---|---|---|
| 1 | Sign off decisions D1–D12. The work already runs on them, but they are still marked "proposed" with the owner boxes unticked | Owner | Boxes ticked, or changes requested. **Current step.** |
| 2 | Close the open measurement items that affect Study A timing: NP-3 (the extra 1.4–1.7 s), NP-4 (full parameter snapshot per run), NP-6 (timing tolerance calibrated before any held-out run) | Agent | Each recorded as resolved, or as a stated limit of the rig |
| 3 | Run the 60 single-event cases and compare each with the model | Agent | Traces committed; D7 verdict recorded |
| 4 | Take the D7 branch. If the model passes, run the 12 paired-event cases (D9) | Agent, owner decides at 4–6 | Branch recorded |
| 5 | Release the benchmark: configurations, harness, traces, model, comparison report | Agent | Tagged release with a README that states the verdict |

The model checker (UPPAAL, decision D8) is only needed for composition
properties beyond Study A. Decide on its licence if and when step 4 passes.

## Not in this version

- ArduPilot or any second autopilot.
- HITL, flight tests and multi-vehicle work. These need hardware, a facility
  and a safety owner (TASKS.md tier 2).
- The per-configuration recovery-envelope comparison from the original plan.
  It can follow a passing Study A.

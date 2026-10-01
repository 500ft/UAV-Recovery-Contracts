# Review index

What to review, and where each piece of evidence lives. The plan is in the
[roadmap](../ROADMAP.md) and the history in the [progress log](SPRINT_PROGRESS.md).
The earlier, longer version of this index is kept at
[commit 236c62b](https://github.com/500ft/uav-failsafe-composition/blob/236c62b0cd796592a38454a19fd87fd3901447f9/docs/REVIEW_READY.md).

Nothing here has had an independent review.

## Review now

1. **Model against PX4's real failsafe class**
   ([differential](../evidence/task-differential-2026-09-29/README.md)). The
   same input sequences go to the Python model and to PX4's compiled `Failsafe`
   class; 11 of 11 agree update for update. Worth checking: whether the
   sequences exercise the parts of the logic Study A depends on, and the stated
   limits (the class's internal delay budget is only observed through its
   effect).
2. **Parameter encoding fix and restored RTL**
   ([runtime record](../evidence/task-runtime-2026-09-29/README.md)). Worth
   checking: the byte-level encoding against PX4's source (linked from the
   record), and the unexplained 1.4–1.7 s between the timers' 15 s and the
   observed RTL.
3. **Study A decisions and the protocol amendment**
   ([decisions](specs/formal-composition/decisions-2026-09-19.md),
   [protocol §7b](specs/formal-composition/study-a-protocol.md)). Signed off on
   2026-09-30. Worth checking: that the coverage gate and the required-cell
   minimum are fixed before the first confirmation run.

## Reproduce

Run the [README quick start](../README.md#quick-start). The tests include a
regression that replays PX4's recorded output against the model. Rerunning SITL
needs the pinned PX4 build described in the
[harness record](../evidence/task-study-a-harness-2026-09-20/README.md).

## Evidence records

**Simulation and model work (newest first)**

| Folder | What it holds |
| --- | --- |
| [task-runtime-2026-09-29](../evidence/task-runtime-2026-09-29/README.md) | Parameter-encoding diagnosis; SITL runs before and after the fix |
| [task-differential-2026-09-29](../evidence/task-differential-2026-09-29/README.md) | Model against PX4's `Failsafe` class, both runs |
| [task-oracle-2026-09-26](../evidence/task-oracle-2026-09-26/README.md) | PX4's own failsafe tests, 9 cases, run on GitHub Actions |
| [task-closeout-2026-09-25](../evidence/task-closeout-2026-09-25/README.md) | Identity, property contracts, shared delay logic, intent audit |
| [task-measurement-repair-2026-09-24](../evidence/task-measurement-repair-2026-09-24/README.md) | Repair of the observation chain |
| [task-study-a-mode-discriminator-2026-09-23](../evidence/task-study-a-mode-discriminator-2026-09-23/README.md) | Offboard-mode hypothesis runs |
| [task-study-a-diagnostics-2026-09-22](../evidence/task-study-a-diagnostics-2026-09-22/README.md) | Runs showing no failsafe for any hazard (before the fix) |
| [task-study-a-verification-2026-09-21](../evidence/task-study-a-verification-2026-09-21/README.md) | First injection run and acceptance checks |
| [task-study-a-harness-2026-09-20](../evidence/task-study-a-harness-2026-09-20/README.md) | Harness build, arming, timing jitter |
| [task-formal-composition-2026-09-19](../evidence/task-formal-composition-2026-09-19/README.md) | Study A contracts and decisions (day 1) |

**Literature and prior art**

| Folder | What it holds |
| --- | --- |
| [task-literature-2026-09-22](../evidence/task-literature-2026-09-22/README.md) | Reading list acquisition |
| [task-prior-art-closeout-2026-09-15](../evidence/task-prior-art-closeout-2026-09-15/README.md) | Prior-art decision and screening |
| [task-2026-09-15](../evidence/task-2026-09-15/README.md), [task-2026-09-12](../evidence/task-2026-09-12/README.md) | Reference coverage records |
| [task-2026-09-11](../evidence/task-2026-09-11/README.md) and the `-clean`, `-clean-network`, `-public` folders | Clean re-acquisition of the database export |
| [task-2026-09-09-review](../evidence/task-2026-09-09-review/README.md), [task-2026-09-09](../evidence/task-2026-09-09/README.md), [task-day3-2026-09-09](../evidence/task-day3-2026-09-09/README.md) | Original search, its provenance correction, and the acquisition ledger |
| [task-2026-09-08](../evidence/task-2026-09-08/README.md) | First-pass source review |

**Setup**

| Folder | What it holds |
| --- | --- |
| [sprint-2026-09-05](../evidence/sprint-2026-09-05/) | First integrity sprint baseline |
| [presentation-2026-09-10](../evidence/presentation-2026-09-10/README.md) | README presentation checks |

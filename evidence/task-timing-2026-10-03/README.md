# Full parameter capture, runtime measurement blocked

The runner captured the complete compiled parameter registry in both attempts.
The new instrumented build failed to reach tracking before any datalink-loss
injection. A control using the saved original executable reached tracking and
responded with Hold then RTL. [results.json](results.json) contains the counts,
timestamps, observed gaps, hashes and failures. This resolves NP-4 for these
captures; NP-3 runtime segmentation and NP-6 calibration remain incomplete.

The [prospective design](design.md) and its [registration](registration.json)
precede execution. Commit `c3b3f66` records the design, runner and instrumented
build before the first launch. After that attempt failed, a
[recorded discriminator](diagnostic-amendment.md) substituted the saved original
executable in a separate control. The remaining registered development labels
were not run. Neither attempt uses a frozen confirmation seed. The control is
not a replacement for a failed calibration repeat.

## What failed

In `dev101`, the ULog's barometer, magnetometer and GPS records end near arming
while ground-truth and local-position records continue. PX4 reports missing
barometer/compass data, loses position validity and selects Descend. The runner
exits at its normal-tracking prerequisite. Its generic normalization reason
`schema_failure` accompanies the explicit `normal tracking was never established`
error; this is not a datalink-response failure.

The original-executable control retains sensor records through its observation
window and completes the injection. The full pre-arm typed parameter values match. This comparison implicates the rebuilt,
instrumented executable as a whole, without isolating instrumentation from the
build environment or establishing a scheduling root cause. No firmware behavior,
compiler warning, permission or safety setting was changed to force a pass.
Further calibration is blocked on a usable instrumented runtime. The failed
capture cannot supply datalink-loss timing, and the control lacks the new
internal receive/decision observations. No upstream PX4 defect is asserted.

## Source trace and observable intervals (NP-3)

All source links below refer to the pinned commit. Source hashes, executable
hashes and the observation-only [patch](instrumentation.patch) are in
[environment.json](environment.json). These are source semantics, not fitted
corrections to the old measurements.

| Stage | Pinned source and clock meaning | Available measurement and limit |
| --- | --- | --- |
| Qualifying heartbeat receive | [`handle_message_heartbeat`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_receiver.cpp#L2142) stamps `now=hrt_absolute_time()` for `MAV_TYPE_GCS` on supported channels | Patch records receive time, channel and sender. Available only in the failed pre-injection attempt. A cached host cut stamp cannot replace this timestamp. |
| Receive to heartbeat aging | [`TelemetryStatus.msg`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/msg/TelemetryStatus.msg#L38) supplies `HEARTBEAT_TIMEOUT_US`; [`CheckHeartbeats`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_receiver.cpp#L2910) keeps the boolean true while elapsed time is at most that timeout | Timeout is 2.5 s; normal age checks are spaced by half that value, with forced checks on accepted heartbeats. These are requested cadences, not scheduling guarantees. |
| Aging to commander timeout anchor | [`publish_telemetry_status`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_main.cpp#L2494) publishes nominally each second or sooner on an update; [`dataLinkCheck`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/Commander.cpp#L2780) sets `_datalink_last_heartbeat_gcs=telemetry.timestamp` whenever the boolean is true | This anchor can advance after the last actual receive. The name does not make it a receive timestamp. The patch logs publications and the consumed anchor; the control does not recover the last qualifying receive. |
| Anchor to detector flag | [`dataLinkCheck`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/Commander.cpp#L2846) tests elapsed time strictly greater than `COM_DL_LOSS_T` | Patch brackets evaluation with entry/exit HRT reads. Commander requests a [10 ms loop](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/Commander.hpp#L217); observed adjacent gaps, not that nominal interval, limit interpretation. The control supplies logged flag samples only. |
| Detector flag to consumed flag | [`rcAndDataLinkCheck`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/HealthAndArmingChecks/checks/rcAndDataLinkCheck.cpp#L75) copies vehicle status into failsafe flags; [commander's loop](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/Commander.cpp#L1866) calls selection before the health check | Health checks run nominally every 100 ms or on status/mode changes. A detector change need not reach selection in the same call. ULog `failsafe_flags` is the logged consumed-input source, not a receive acknowledgment. |
| Consumed flag to selected action | [`FailsafeBase::update`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/failsafe/framework.cpp#L53) uses its update-time argument and the shared action delay | Patch records update entry and post-selection HRT, plus action/delay state. Control console announcements identify Hold/RTL but do not continuously observe selection. No selector timestamp is inferred from an announcement. |
| Selection to committed nav_state | [`handleModeIntentionAndFailsafe`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/commander/Commander.cpp#L2366) maps action, applies replacements and records `nav_state_timestamp` after a change | Patch has a separate post-commit HRT read. The control preserves `nav_state_timestamp` and first logged status. The reported logged-flag-to-RTL interval is only this combined middle segment. |
| Commitment to navigator response | [Navigator loop](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/navigator/navigator_main.cpp#L167) wakes on local position, status or mission, selects a mode, runs it and publishes updated setpoints | Local-position wakeup is rate-limited to 50 ms; the poll timeout is 1 s. Patch brackets mode execution/setpoint publication, separately from status receipt. Control ULog navigator/status/setpoint records are retained with their observed gaps, but do not give that execution bracket. This says nothing about maneuver completion. |

The source identifies an omitted heartbeat-aging/publication segment before the
configured commander timeout. It explains why adding the two parameter timers
is not a complete receive-to-RTL model. It does not reconstruct the exact
residual in the historical runs, whose last receive was not logged. All native
instrumentation uses one vehicle HRT clock per process boot; identical clock
values do not prove simultaneous execution, and logging may perturb scheduling.

## Parameters and calibration limits

`parameters-full.json.gz` contains typed reads of the full generated registry,
including unused entries, plus transport bytes and registry hashes. The name/type
set was checked against the compiled parameter enum. No default substitutes for
a missing read; an interrupted capture remains incomplete and blocks arming.
The full snapshot hash is part of each trace's execution artifact identity.
The historical `overrides_readback_complete` field remains false because its
hash still covers only overrides. These sequential pre-arm snapshots do not
certify constancy in flight. The two runs have separate parameter/clock identities.

NP-6 produced no replacement tolerance. Host stream cessation still has no
vehicle-clock upper bound under D23/D24; a subsequent telemetry packet cannot
supply one. Even with a successful receive-to-response trace, that interval
would differ from host-cut-to-response latency. Historical tolerances remain
unchanged, and timing stays outside pass/fail under signed protocol section 7b.
No complete-chain calibration, confirmation result or general equivalence is claimed.

## Reproduction

The exact build/run commands and execution order are in `environment.json`.
The native source was restored clean and the saved original executable restored
byte for byte. Both original and instrumented executables remain in the external
cache named there. Compressed raw telemetry, ULogs, console logs, cases,
snapshots and normalized traces are retained here without modifying their bytes.

```sh
python evidence/task-timing-2026-10-03/analyze.py
# Re-extract the compact ULog observations with pyulog installed:
python evidence/task-timing-2026-10-03/analyze.py --extract
```

The control also retains the first logged navigator RTL status and the first
subsequent valid setpoint publication. Status is published after the navigator
mode loop ([source](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/navigator/navigator_main.cpp#L895));
these are response observations, without the direct execution entry/exit
bracket. Equal HRT stamps indicate clock resolution, not zero wall latency.

The first command reproduces `results.json`. The second also re-derives the
ULog counts, gaps and transitions. `checks.json` records local verification.
The next step is to diagnose the instrumented runtime's tracking failure before
completing NP-3/NP-6 or starting the signed Study A cells.

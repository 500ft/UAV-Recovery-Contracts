# The uninstrumented rebuild completes the control

The matched rebuild completed tracking, datalink loss, Hold, RTL and landing.
Its full typed pre-arm parameter values match both prior attempts. Rebuilding
the affected sources alone did not reproduce the earlier instrumented failure
in this run. [results.json](results.json) holds the executed counts, comparison,
observed sensor gaps, mode transitions and artifact hashes.

The specific instrumentation repair remains unresolved. No additional simulator
attempt or timing observation was run after this control, and no firmware or
runner behavior was changed. The earlier failed attempt remains in the
[task-3 packet](../task-timing-2026-10-03/README.md).

## Matched build and execution

The [design](design.md) and [registration](registration.json) were recorded
before execution. Commit `6af9585` records them and the completed build before
launch. Development label 201 uses the same explicit schedule offset, Auto
Loiter RTL configuration, full typed snapshot and runner as the earlier
attempts. No confirmation seed was consumed.

The pinned checkout was clean. Every translation unit rebuilt for the prior
instrumented executable was explicitly touched and recompiled with compiler
cache reuse disabled for this command. The [verbose build log](build.log)
contains the compiler invocations and link command; [rebuild.json](rebuild.json)
records their source/object identities and the resulting binary hash. This ran
the newly linked executable, whose hash differs from both saved executables.
Untouched objects were reused from the existing build; this was a rebuild of
the affected units, not a clean rebuild of the entire firmware.

[dependencies.json](dependencies.json) records shared-library identities, sensor
source/object hashes and the recursive submodule-state hash. The submodules
match their recorded commits. Build configuration and compiler flags were kept
unchanged; no warning was suppressed. Copies of CMakeCache, Ninja metadata,
compile commands and submodule status remain in the external cache, with hashes
in registration. The saved original and instrumented binaries were preserved.

## What the scheduling trace establishes

The simulated
[barometer](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/simulation/sensor_baro_sim/SensorBaroSim.cpp#L40),
[magnetometer](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/simulation/sensor_mag_sim/SensorMagSim.cpp#L41)
and [GPS](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/simulation/sensor_gps_sim/SensorGpsSim.cpp#L42)
use `hp_default`. Their periodic scheduling goes through
[`ScheduledWorkItem`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/platforms/common/px4_work_queue/ScheduledWorkItem.cpp#L58),
and the [work queue](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/platforms/common/px4_work_queue/WorkQueue.cpp#L174)
executes callbacks serially. A blocked callback could therefore affect all
three. Their ULog records continue through this control's observation window.

The prior observation patch uses `PX4_INFO`, which both writes console output
and [publishes a uORB log message](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/platforms/common/px4_log.cpp#L181).
These are possible sources of observation overhead. Neither the prior ULog nor
its console capture records the worker's stack, scheduling state or callback
entry/exit at the sensor interruption. The available evidence cannot identify
a blocked callback, a logging call or a transport/scheduling mechanism as the
cause. Reducing logging or changing simulator behavior would therefore be an
untested guess. No such repair or further campaign was attempted.

## Remaining measurement limit

The successful uninstrumented control qualifies neither the failed observation
patch nor a replacement. Last qualifying receive, detector evaluation and
continuous selection remain unavailable together on a successful run. The
registered development timing observations remain pending. NP-6 has no new
tolerance, and host cessation still has no vehicle-clock upper bound under the
signed protocol. Logged flag, mode and sensor samples describe only their
observed intervals; the retained adjacent gaps are not hard scheduling bounds.

The next technical requirement is to localize the instrumented runtime's sensor
interruption before selecting a repair and resuming the registered observations.
This task stops at that blocker. There was no Study A confirmation or release.

## Reproduction and restoration

```sh
python evidence/task-runtime-rebuild-2026-10-03/analyze.py
# With the existing pyulog dependency, re-extract observations as well:
python evidence/task-runtime-rebuild-2026-10-03/analyze.py --extract
```

Both commands reproduce `results.json`; extraction reuses the prior packet's
ULog reader. The exact run command is in registration. All raw run files are
retained, compressed without changing their bytes. [restoration.json](restoration.json)
records the clean pinned source and byte-for-byte restoration of the saved
original executable. The newly rebuilt executable remains in the external
cache. [checks.json](checks.json) records local validation.

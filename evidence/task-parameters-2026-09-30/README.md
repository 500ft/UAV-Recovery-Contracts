# Full parameter capture

The development run captured the full parameter table before arming and after
the observation window. Both snapshots cover every entry reported by the running
firmware. The snapshots agree on the requested overrides. The differences are
the flight identifier and accumulated flight time. The run entered RTL and then
landed.

[results.json](results.json) holds the counts, differences, capture durations,
binary identity and artifact hashes. Reproduce it with:

```sh
python evidence/task-parameters-2026-09-30/summarize.py
```

## Capture procedure

The runner calls the native `param show -a` command for the names, indices and
total count. It requires a unique name for every index in that table. It then
reads each value using PX4's typed MAVLink transport and retains the type with
the decoded value. A missing entry or failed read leaves a partial snapshot
and stops the run. The execution identity includes the snapshot file hashes.
The override readback remains separately identified.

The native table includes unused parameters that `PARAM_REQUEST_LIST` omits.
The shell's printed float values are rounded; only its names and indices are
used. The typed reads supply the values. These behaviors are in the pinned
[parameter command](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/systemcmds/param/param.cpp#L532)
and [MAVLink parameter implementation](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/mavlink/mavlink_parameters.cpp#L422).

[environment.json](environment.json) records the exact command, repository
base and approved protocol hash. The `run` directory retains both inventories,
typed snapshots, case, summary, raw telemetry, console output, autopilot log
and normalized trace. Original logs are gzip-compressed without alteration.

## Scope

NP-4 is complete for this local SITL runner. The snapshots are sequential reads,
so they record coverage over each capture interval rather than an atomic state
or a continuous record of every parameter change. The approved gate and seeds
are unchanged. This is development evidence and contributes no confirmation
cells. NP-3 and NP-6 remain the next measurement items in the roadmap.

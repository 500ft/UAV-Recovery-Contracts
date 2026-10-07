# Observation qualification

Run one matched development pair before deciding whether Study A can start.
The prior cache-disabled control recompiled selected uninstrumented units;
its record contains no fresh cache-disabled instrumented build.

Use the pinned PX4 source and installed compiler in separate initially empty
build directories. Disable compiler caching for configuration and compilation.
Build the `px4` target with the existing default SITL board and RelWithDebInfo
flags. Preserve warnings and the saved original, instrumented and rebuilt
executables. First build and run the uninstrumented control, then apply the
unchanged task-3 observation patch, build and run the instrumented member.
Restore that exact patch after use. Both runs use development label 301,
explicit offset zero, Auto Loiter, the RTL configuration, datalink loss and full
typed pre-arm parameter capture. Fresh processes and working directories are
the units; ticks are not independent observations. No public log or held-out
sequence is used. The scenario, source, patch, protocol and runner hashes are
registered before execution; executable/configuration hashes precede launch.

Record build failures, launch failures, parameter differences, tracking and
injection stages, sensor/topic gaps, ULog dropouts, available CPU/load reports
and all available event-to-mode clock segments. Compare discrete outcomes and
typed parameter values exactly for this pair. Timing is descriptive, with no
new tolerance or timing verdict. Nominal publication cadence is not a bound on
scheduling delay. An unchanged topic value does not expose every selector call.
A successful clean build cannot establish stale compiler cache as the cause.

If source instrumentation disrupts tracking, inspect the pinned logger's
subscription defaults and actual topics. At most one additional logger-only
qualification pair is allowed if a specific available logging option can
resolve a remaining observation requirement. Register its precise change and
hashes before either run. Do not run it merely to collect more evidence when
unpublished selector state already defeats that proposed remedy. No open-ended
scheduler debugging or model expansion is authorized by this design.

Before confirmation, apply signed protocol section 7b, D7 and D23/D24
precisely. Timing calibration is not a pass/fail prerequisite for discrete
agreement, but valid event observation, declared supported mechanisms and all
required configuration cells remain mandatory. Inspect the complete required
cell rule, existing model/adapters and event channels. Only if those gates are
met, commit D25 cell identities and freeze source/build/parameters, harness,
model/adapters and comparison before executing required confirmation seeds.
Otherwise retain this qualification result and stop. A post-freeze repair ends
that confirmation attempt. No replacement seed, hazard-pair campaign or release.

# Matched rebuild control

Before execution, rebuild the clean pinned PX4 source in the installed native
SIH build environment. Force recompilation of every translation unit rebuilt
for the previous instrumented executable, bypassing compiler-cache reuse for
this command. Keep flags, generated build configuration and dependencies fixed.
Save build commands, object/source hashes and executable identity. Preserve the
saved original and instrumented executables from the previous diagnostic.

Execute one uninstrumented rebuild control with development label 201, explicit
offset 0, the existing Auto Loiter RTL datalink-loss configuration and full typed
parameter capture. Compare with both retained task-3 attempts, including full
parameter values, setup stages, sensor observation gaps and mode transitions.
This uses no confirmation seed. Keep every attempt, including unsuccessful ones.

Inspect the sensor scheduling paths and build/dependency/cache identity before
attributing the failure to logging. If this control identifies a specific
repair, make the smallest correction and one matched verification. If runtime
observation recovers, finish only the previously registered development timing
observations. Otherwise stop at the remaining blocker; do not run a speculative
campaign. Restore the pinned source and saved original executable afterward.

No change to PX4 behavior, warnings, safety settings, host permissions, signed
timing criteria or historical evidence is allowed. Host stream cessation still
has no vehicle-clock upper bound. No Study A confirmation or release occurs.

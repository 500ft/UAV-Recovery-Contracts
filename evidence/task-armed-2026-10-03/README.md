# Armed-state differential

The disarmed audit failed before the fix and agrees after it. Read the
[before report](before/report.json) and [after report](after/report.json) for
per-sequence comparisons and transition times. The original differential
[evidence](../task-differential-2026-09-29/README.md) is unchanged.

The driver had parsed `armed` without applying it. The selector also returned
before updating timers while disarmed. It now processes arming transitions,
condition state and delay bookkeeping before choosing the action. A cleared
condition and its latched action have separate state: pinned PX4 removes the
eligible latch on either arming transition only if the condition was already
clear on the preceding update. An active condition can survive disarm and
resume its action on rearm. Terminate remains latched.

The focused [sequences](../../oracle/differential/armed-sequences) exercise
initial disarm, disarm during a pending delay, disarm after RTL, conditions
cleared before or with disarm, conditions cleared while disarmed, rearm, a
geofence latch, and Terminate raised before or during disarm. The adapter now
applies an initial `armed` directive before construction. Later directives
still take effect on the next update. The native failsafe source is unchanged.

## Recorded limitation

`position-disarm-rearm` disagrees: its default mode is POSCTL and its
`COM_POS_LOW_ACT` is 3. Pinned
`failsafe.cpp` checks `position_accuracy_low` only in Auto Mission or Auto
Loiter; the Python driver ignores that restriction. Its model and native
outputs remain in the after report and the full corpus denominator. Under
[D7](../../docs/specs/formal-composition/decisions-2026-09-19.md), claims for
`position_accuracy_low` in this mode and configuration, including disarm and
rearm, remain blocked. This mode-eligibility gap belongs to the next
supported-domain task. All agreement statements here concern selected
actions on the exercised corpus. No integrated runtime, Study A or broad
random campaign was run.

## Native build and identity

[environment.json](environment.json) identifies the pinned source, compiler,
ASAN runtime, and both adapter binaries. Each executable contains the
repository's test adapter and local build instrumentation. Neither is an
upstream test binary. The CMake [instrumentation patch](instrumentation.patch)
registers the adapter and sets a link option on that target only. Copy the
corresponding repository adapter into the pinned failsafe source directory
before applying the registration, as in
[run_differential.sh](../../oracle/run_differential.sh).

The targeted build used:

```sh
CCACHE_DIR=/Users/redhose/.cache/uav-failsafe-composition/ccache \
  cmake --build build/px4_sitl_test --target functional-differential_delay_test
```

The original target built but aborted at launch. The installed SDK exposed
`___asan_get_report_description` through libSystem, while the running OS lacked
that export. Clang's installed ASAN dylib supplied the symbol. The
[original compiler command](original-command.json) places `-lm` before the
compiler-added ASAN library, allowing libSystem to claim the symbol first.
The installed linker's manual states that libraries are searched in command
line order.

The single environment correction puts the matching ASAN dylib first, using
`target_link_options(functional-differential_delay_test BEFORE PRIVATE
"<compiler runtime>/libclang_rt.asan_osx_dynamic.dylib")`. The compiler runtime
path comes from `/usr/bin/c++ --print-runtime-dir`. The
[final command](link-command.txt), [undefined ASAN imports](symbol-bindings.txt)
and [build log](build.log) record the result. The symbol listing retains only
the undefined ASAN imports that identify the runtime binding. The verbose
listing is preserved at
`/Users/redhose/.cache/uav-failsafe-composition/runs/armed-task1-20261003/symbol-bindings-verbose.txt`.
Sanitizers, two-level symbol binding
and compiler warning flags remain enabled. No PX4 behavior, global toolchain
setting, permissions or runtime approvals changed. Hashes use Python hashlib.

The original adapter was rebuilt under this same correction to record its
binary identity and repeat the before traces. Both audit CSVs were identical
to the successful pre-implementation reproduction. The final adapter was
then rebuilt and the entire recorded corpus rerun with its identified binary.

## Repeating the comparison

With the recorded build environment and adapter in place, run each sequence
in a separate process. Set `BIN` to the built target and `OUT` to a fresh output
directory, then run from the repository root:

```sh
mkdir -p "$OUT"
for seq in oracle/differential/sequences/*.seq oracle/differential/armed-sequences/*.seq; do
  name=$(basename "$seq" .seq)
  ORACLE_SEQUENCE="$PWD/$seq" ORACLE_OUT="$OUT/$name.oracle.csv" \
    "$BIN" > "$OUT/$name.native.log" 2>&1 || exit 1
  python3 oracle/differential/driver.py model "$seq" "$OUT/$name.model.csv" || exit 1
done
python3 oracle/differential/driver.py report "$OUT" --seq-dir oracle/differential/sequences
python3 oracle/differential/driver.py report "$OUT" --seq-dir oracle/differential/armed-sequences
```

The reports expose disagreements; a successful process exit alone does not
mean agreement. [Unknown-command results](unknown-command.json) and the
[native log](unknown-command.native.log) verify the existing rejection in both
adapters. Offline regression tests in
[test_differential.py](../../tests/test_differential.py) compare the fixed
model with the recorded native actions and preserve the counterexample.

CSV and log line endings and trailing whitespace were normalized for git.
CSV values were checked unchanged; raw files remain in the local run cache.

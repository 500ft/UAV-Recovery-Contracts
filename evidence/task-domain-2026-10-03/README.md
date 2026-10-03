# Declared-domain differential

The frozen implementation agrees with the fresh reserved corpus. The full
[results](results.json) separate directed development, random development,
model replay after fixes, fresh native verification, and excluded admission
probes. They report attempted, excluded, invalid, executed and disagreeing
sequences by mechanism. Action exposure is counted by sequence, including
all-None sequences. Development and reserved inputs have no identical inputs
within or between their sets.

Development exposed adapter mode eligibility and model action-option errors.
The [disagreement index](development-disagreements.csv) retains every failing
development identity. The classification uses the eligibility-only replay to
distinguish adapter-only failures from remaining model failures; cases changed
by eligibility but still failing are marked `adapter_and_model`. All were
resolved in development. No mismatch was attributed to native behavior or
removed from the denominator.

| Reproducer | Root cause and repair |
| --- | --- |
| [position-mode](counterexamples/position-mode.seq) | Gate position accuracy by the mode check in pinned PX4. Among admitted modes, only AUTO_LOITER checks it. This resolves the task 1 POSCTL defect. Disabled datalink loss also skips registration, as in the native source. |
| [position-delay](counterexamples/position-delay.seq) | Position actions do not seed a delay because their takeover option is AlwaysModeSwitchOnly. They can still share an existing delay. |
| [warning-clear](counterexamples/warning-clear.seq), [disarm-clear](counterexamples/disarm-clear.seq) | Warn, None and Disarm use the default WhenConditionClears option. Clear their actions when their condition clears. |
| [hold-seeds-delay](counterexamples/hold-seeds-delay.seq), [none-seeds-delay](counterexamples/none-seeds-delay.seq) | Auto takeover options seed the shared timer even for link Hold and geofence None. The ability to delay an action is a separate selection rule. |

[Counterexample comparisons](counterexamples.json) preserve native outputs and
both model versions. Representatives were isolated from the observed mechanisms
and source rules, then reduced by command deletion and whole-tick duration
reduction. Parameters stayed fixed; AUTO_LOITER was kept for the eligible-position
case so it could not collapse into the separate POSCTL defect. Every remaining
non-parameter command deletion was tested, subject to that mode precondition.
[Minimization details](minimization.json) record the procedure and its limits.

The [verification freeze](verification-freeze.json) precedes execution of the
reserved inputs. There were no implementation changes after those results.
The checked-in reserved examples are index zero in each stratum, selected by
identity rather than outcome. The original task 1 evidence remains unchanged;
its historical mismatch stays asserted beside the new passing comparison.

## Interpretation under D7

The task 1 POSCTL position-accuracy discrepancy is resolved for the exercised
configuration and traces. No discrepancy remains in the executed admitted corpus.
The exclusions below remain outside supported claims. Agreement is a result
for these generated sequences, parameters and tick schedules, not universal
equivalence or a population success rate. No timing experiment or Study A ran.

## Raw evidence

[archive.json](archive.json) identifies the external compressed raw record.
It includes all input seeds and hashes, native CSVs and logs, baseline and fixed
model outputs, comparisons, frozen generator, baseline source and minimization
runs. Development after-fix comparisons replay the model against the already
executed native outputs; reserved comparisons execute a fresh native process
for each sequence. [Environment](environment.json) identifies the reused native
binary and unchanged adapter. The pinned native checkout was clean throughout.
The compact repository record keeps root-cause traces and deterministic reserved
examples, rather than checking in every native log.

## Domain recorded before execution

The machine-readable values and campaign sizes live in [campaign.json](campaign.json).
[registration.json](registration.json) records the generator, parameter file and
complete generated corpus hashes before either corpus was executed. Development
and reserved seeds are separate. The unit is one independent sequence with a
fresh native process and Python selector, not a tick.

| Item | Admitted campaign domain and source |
| --- | --- |
| Firmware and native binary | Pinned source and the `after` binary in [task 1 identity](../task-armed-2026-10-03/environment.json). The task 1 adapter and target-local ASAN ordering are reused unchanged. |
| Parameters | Enumerated values in `parameters` and `fixed_parameters` in [campaign.json](campaign.json). Supplied values are set before construction; omitted values use the pinned defaults (the corresponding model values are in `model/px4_failsafe.py:DEFAULTS`). Generated sequences set every listed parameter; directed cases may omit action parameters. Other native parameters retain pinned defaults; their input conditions remain false. Tables follow `failsafe.cpp` `fromNavDllOrRclActParam`, `fromGfActParam`, `fromPosLowActParam`. |
| Flags | Boolean GCS loss, geofence breach and position accuracy loss, named in the configuration. All other flags and mode-requirement masks stay zero, as initialized by `differential_delay_test.cpp`. RC loss is excluded. |
| Modes | One fixed mode per sequence from the configuration. An optional initial mode directive is applied on the next update; construction uses POSCTL. Only AUTO_LOITER enables position-accuracy checking among these modes (`failsafe.cpp` lines 546–550). AUTO_MISSION is absent from the native parser and excluded. |
| Arming and landed state | Initial armed or disarmed; subsequent disarm and rearm allowed. The native adapter supplies rotary-wing type, no VTOL transition, mission unfinished. Neither adapter exposes landed state; no landed-state or landing-completion claim. |
| Commands | `param`, optional initial `mode`, `flag`, `armed`, `run`; no parameter changes after construction, no mode changes after running, no unknown commands or extra tokens. |
| Ticks | Positive whole update counts at the configured millisecond tick sizes. Initial update is at the existing adapter's start time; changes apply at the next update. Durations with fractional ticks are excluded to avoid Python round versus C++ lround differences. Per-sequence update limit is in the configuration. |
| Reset and selection | Fresh process and selector for each sequence; fixed parameters and initially false flags. Compare every timestamp and selected action exactly. No tolerance or population estimate. |
| Exclusions | RC optional-at-arming state; changing modes, pilot stick takeover, deferral, Offboard-loss flags, mode fallback/invalid navigation estimates, battery, wind, motors, VTOL/fixed-wing, mission completion, runtime parameter updates, integrated commander/navigator or physical dynamics. OFFBOARD here is only a fixed mode with its loss flag false. |

The campaign's [admission function](../../oracle/differential/campaign.py) uses
the existing parser and rejects the same input before **either** adapter runs.
The standalone adapters retain the wider legacy sequence grammar for regression
replay; accepting a sequence directly is not a supported-domain claim. This
is an input restriction for this executed campaign, not a general parser or
fuzzing interface.

The native source registers GCS, position and geofence actions in
`failsafe.cpp` lines 515–562. `framework.cpp` lines 61–89 order latch removal,
delay updates, action registration and selection. Lines 304–430 define
registration and clear conditions; lines 438–535 select actions and delay them.
These source rules also govern conditions that clear and reassert and arming
transitions. State present there can be added to the model when needed.

## Reproduction

Use the cached Python identified in registration and the task 1 native binary.
The generator uses independent per-sequence `random.Random` seeds; the manifest
contains each seed and input hash. The configured strata exercise delay boundaries,
simultaneous flags, ordered flags, clear/reassert and arming. Random tails add
short flag changes, and arming tails also toggle armed state. Directed sequences
precede development execution. Reserved inputs are generated and hashed at the
start but executed only after the implementation is frozen.

```sh
python oracle/differential/campaign.py generate evidence/task-domain-2026-10-03/campaign.json "$CORPUS"
python oracle/differential/campaign.py run evidence/task-domain-2026-10-03/campaign.json "$CORPUS/directed" "$BIN" "$OUT/directed"
python oracle/differential/campaign.py run evidence/task-domain-2026-10-03/campaign.json "$CORPUS/development" "$BIN" "$OUT/development"
# Run the reserved corpus once, after freezing the implementation.
python oracle/differential/campaign.py run evidence/task-domain-2026-10-03/campaign.json "$CORPUS/reserved" "$BIN" "$OUT/reserved"
```

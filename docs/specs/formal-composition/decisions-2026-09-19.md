# Frozen decisions for the first software study — 2026-09-19

Status: **signed off 2026-09-30** (see the last addendum). Originally proposed by the agent, awaiting owner sign-off. A proposed value is not a frozen value. Sign off by editing the Owner column in this PR; every value with "owner" outstanding blocks the task named beside it. Decisions D1-D6 and D10-D12 are already realised in the files cited; D7-D9 and D13 need your answer before the corresponding day's work.

Base: main `929cc8a` (the merge of PR #6, merged 2026-09-16). Critique of the handoff that produced these: [plan-critique-2026-09-19.md](plan-critique-2026-09-19.md). Baseline sources cited as `[Bn]`: [docs/baselines/README.md](../../baselines/README.md).

| id | decision | frozen value | basis | blocks | owner |
|---|---|---|---|---|---|
| **D1** | PX4 identity | `v1.17.0`, commit `d6f12ad1c4f70ad3230afd7d86e971421e02fef4`, built here as `px4_sitl_default` | newest tagged release that built and launched in this environment; not chosen from documentation [B1][B10] | everything | ☑ 2026-09-30 |
| **D2** | Vehicle model | `10040_sihsim_quadx` — PX4's simulation-in-hardware quadrotor, no external physics simulator | fewest moving parts, no Gazebo dependency, ships with the pinned release; mass 1.0 kg, inertia diag(0.025, 0.025, 0.030) [B10] | URC-02 | ☑ 2026-09-30 |
| **D3** | Simulator mode | lockstep enabled (default for `px4_sitl_default`) | deterministic simulation time; note that it does **not** make host-side injection deterministic, see D6 | URC-04 | ☑ 2026-09-30 |
| **D4** | Event classes (six, all injectable) | offboard loss (stop the setpoint stream), datalink loss (stop GCS heartbeats), RC loss (stop `MANUAL_CONTROL`), GPS/estimator-validity loss (`failure gps off`), battery (`failure battery wrong` at `SYS_FAIL_BAT_LVL`), geofence breach (`GF_MAX_HOR_DIST` + commanded fly-out) | each has a distinct, repeatable stimulus [B3][B4]; **the handoff's "setpoint-only loss" is not separable over MAVLink** and is deferred, see D11 | URC-02, URC-04 | ☑ 2026-09-30 |
| **D5** | Configuration variants | one intention family per row: vendor defaults, Hold, RTL, Land, plus two one-factor timer variants (`COM_FAIL_ACT_T=0`, `COM_DL_LOSS_T=5`) | one-factor changes only; the equivalence rule is computed from the pinned parameter maps, not asserted | URC-02 | ☑ 2026-09-30 |
| **D6** | Injection scheduling | on **vehicle** time: wait for a telemetry timestamp to cross the scheduled value, then inject; record scheduled and observed vehicle timestamps | lockstep does not bound host-side UDP jitter (critique finding 7) | URC-04 | ☑ 2026-09-30 |
| **D7** | Agreement decision rule | by count, not percentage: **≤3** disagreements of 60 → proceed; **4-6** → owner decision with every disagreement root-caused; **≥7** → kill the formalisation and release the benchmark. Report a Wilson 95% interval beside every agreement figure | 95% of 60 is 57 runs; the plan's 95%/90% boundary is one run wide (critique finding 5) | Study A analysis | ☑ 2026-09-30, as replaced 2026-09-25 |
| **D8** | Checker | **not available.** `verifyta`/UPPAAL is absent on this machine and needs an accepted academic licence. Options: (a) accept the UPPAAL academic licence and pin its version, (b) build the model and queries now and defer checking, (c) name a different timed-automata checker | no homemade reachability engine, per the handoff's own rule | Study B | ☑ 2026-09-30: option (b) |
| **D9** | Paired-event tier | after the 60 single-event cases: 4 ordered hazard pairs × 1 configuration × 3 seeds = 12 cases; until they pass, any checker prediction that depends on two simultaneous hazards is a hypothesis | U2 and U3 are defined over simultaneous hazards; a single-event matrix cannot validate them (critique finding 4) | Study B interpretation | ☑ 2026-09-30, as replaced 2026-09-25 |
| **D10** | Paths | `protocols/configuration-matrix.{json,md}`, `protocols/trace-schema.json`, `protocols/unsafe-composition-properties.json`, `model/`, `harness/` | the handoff proposed `tools/sitl/` and different protocol filenames; `tools/` already holds the presentation checkers CI runs, and the contracts were built on 2026-09-16 under these names. The handoff permits recorded deviations | — | ☑ 2026-09-30 |
| **D11** | Deferred: setpoint-only loss | needs a uXRCE-DDS/ROS 2 offboard path so the keep-alive and the setpoint topics are separable [B4]. Trigger: the single-event tier passes and the ROS 2 path is available in this environment | — | — | ☑ 2026-09-30 |
| **D13** | RC loss is not injectable in this rig | Recorded as a frozen class that the campaign excludes, not deleted. PX4 in SIH SITL did not accept MAVLink `MANUAL_CONTROL` as a manual-control source (2026-09-20: `manual_control_signal_lost` stayed true while the stream ran at 10 Hz), so there is no RC signal to remove | a class with no stimulus cannot be a case; the alternative is a simulated RC source or a joystick bridge | Study A coverage | ☑ 2026-09-30: five injectable classes |
| **D12** | Horizon and tolerances | horizon = injection + 45 s or terminal mode, whichever first; timing tolerance unchanged from the protocol (median \|Δt\| ≤ 0.2 s, p95 ≤ 1.0 s) | 45 s covers `COM_DL_LOSS_T` + `COM_FAIL_ACT_T` + an RTL from 60 m with margin [B10] | Study A | ☑ 2026-09-30 |

## 2026-09-21 addendum

Section 12 of the handoff added acceptance checks; where each one lives is recorded in
[section-12-acceptance-2026-09-21.md](section-12-acceptance-2026-09-21.md). Two of them changed what these
decisions mean:

- **D4 (event classes)** now has an open question of its own. The first controlled injection of `datalink_loss`
  on the frozen configurations produced no failsafe action at all, with the monitor confirmed active. Until
  that is resolved, no event class is known to produce an action in this rig, and the campaign in D7 should not
  start. Evidence and the named diagnostics: [task-study-a-verification-2026-09-21](../../../evidence/task-study-a-verification-2026-09-21/README.md).
- **D12 (tolerances)** is unchanged, but the timing comparison is now made relative to the injection instant
  and the hazard timer is known to start from the last heartbeat *received*, up to one heartbeat period before
  the harness stops sending.

## 2026-09-22 addendum

The two diagnostics named on 2026-09-21 were run, and a third. The finding is wider than the original
refutation: **the failsafe framework selects no action for any hazard tested in this configuration**, across
two monitors, three parameter settings, and an action that can be neither delayed, deferred nor taken over.
Parameter delivery, the Hold delay, user takeover, deferral, land detection and arming are all eliminated.
Evidence: [task-study-a-diagnostics-2026-09-22](../../../evidence/task-study-a-diagnostics-2026-09-22/README.md).

Consequences for these decisions: **D7's campaign stays held**, and D4's event classes are all affected, not
just one. Nothing about the rig is known to be able to produce a failsafe yet, so no agreement rate can be
measured and Study B has nothing to validate against.

## 2026-09-23 addendum

The Offboard hypothesis is eliminated: the same datalink loss in Auto Loiter also produces no action, on a
valid run with the hazard confirmed. Evidence:
[task-study-a-mode-discriminator-2026-09-23](../../../evidence/task-study-a-mode-discriminator-2026-09-23/README.md).

The critical path is now the offline oracle, which needs Linux. The GPU host at hand is Windows 11 Home
**without WSL**, so a new decision is needed:

| id | decision | options | blocks |
|---|---|---|---|
| **D14** | Where to run the offline failsafe oracle | (a) install WSL on the GPU host, which is a system change and a restart on a machine with no monitor; (b) use another Linux machine; (c) leave the oracle unrun and accept that the cause stays unidentified | Study A, and therefore Study B and C |

## Seeds

Frozen before any validation run: `1, 2, 3, 5, 8` for the single-event tier; `11, 13, 17` for the paired tier. SIH is deterministic given the same parameters, so the seed varies only the injection time within a ±2 s window around the scheduled vehicle time; the window is part of the case ID.

## What is not decided here

Whether the formal-composition direction succeeds; anything about ArduPilot, hardware, HITL, flight, or fleets; the prior-art distinctiveness statement (URC-01 is partial and the formal axis is unsearched); and whether any confirmed interaction is reported upstream, which needs a separate disclosure review.

## 2026-09-24 addendum — measurement repair

The owner's 2026-09-24 literature critique, delivered as
`LITERATURE-CRITIQUE-AND-REVISED-PLAN-2026-09-24.txt`, was assessed against the code; the assessment is
[critique-2026-09-24.md](critique-2026-09-24.md) and the packet is
[task-measurement-repair-2026-09-24](../../../evidence/task-measurement-repair-2026-09-24/README.md).

Eleven of its twelve findings hold. Three were live defects in the observation chain and are fixed: the
normaliser overwrote the vehicle's own injection-time reading with a host estimate; the verifier compared
pre-injection setup transitions against the expected recovery and returned `refuted` for identity and validity
failures; and the trace could not distinguish PX4's `Action::None` from not observing the selector.

Re-deriving all ten stored captures from their raw data leaves every substantive conclusion in place. The four
valid control repeats now verify instead of being unassessed; the five injected runs stay refuted, with an
empty response window rather than a mismatch against takeoff. The observation survives the repair, at
its supported strength: No expected post-injection recovery-mode transition was observed and no new failsafe announcement was seen; the internal selected action and its cause remain unresolved. The selector is not on any channel this rig records, so `selected_action` is `unobserved`, and an absent announcement is not a continuous record of selector state (owner review 2026-09-25, R4).

New decisions and open items:

| id | decision | status |
|---|---|---|
| **D15** | A verdict is `unverified` when the comparison could not be made, `inconclusive` when an estimated instant straddles the deadline, and `refuted` only when a valid observation contradicts a prediction | decided here |
| **D16** | A host-only instant is bounded by the nearest real vehicle-clock readings either side of it; the offset spread is reported as a dispersion and never used as an uncertainty | decided here |
| **D17** | U4's `expected_manoeuvre_time` divides distance by a maximum speed, which is a lower bound on time used as a deadline. U4 must not be evaluated against measured runs until it is replaced | open, belongs with the F5 property rewrite |
| **D18** | `T6` added: the Auto Loiter control timeline, whose expected post-takeoff sequence is `AUTO_LOITER` | decided here |

D14 is unchanged and still blocks Study A. D7, D9 and D13 still need owner answers.

## 2026-09-24 addendum 2 — consistency follow-ups

Four places where the repair left the repository saying two different things. None changed a result.

| id | item | decision |
|---|---|---|
| **D19** | `protocols/event-semantics.md` described the clock offset as estimated from the first 10 heartbeats, which stopped being true on 2026-09-21 | amended with a dated §7; §2's `native_transition` definition was already correct and the code had disagreed with it |
| **D20** | The frozen 1.5 s tolerance cited a 0.51 s jitter measured through the old clock conversion; on the vehicle's own clock the same runs give 0.352 s | the **value stays frozen**; only the basis text is corrected. Re-deriving a tolerance downward against the data it must judge is fitting |
| **D21** | `harness/reproducibility.py` pooled reconstructed and measured instants into one spread, and that spread is what D20's figure came from | spreads are reported per clock source and never pooled; only a `measured` spread may be quoted as apparatus jitter |
| **D22** | The 21, 22 and 23 September evidence records state pre-repair verdicts | kept verbatim, each given a dated pointer to the re-derivation; historical records are not rewritten |

Still deferred from the critique's TASK 2, and not attempted here: scenario identity including the event
schedule, the complete applied-parameter hash and the build identity, and compatibility mappings for
historical case IDs. Only the intended-mode part of that item is done.

## 2026-09-25 addendum — owner review of PR #29, and the decisions it settles

The owner reviewed PR #29, reproduced three defects in it with in-memory probes, and supplied
`TODAY-CLOSEOUT-PLAN-2026-09-25.txt`. All three reproduce here exactly as reported. They are mine.

| id | decision | status |
|---|---|---|
| **D16** | **Revised.** A received stamp bounds a later instant BELOW only. A packet can be delayed past the instant, so the next stamp does not bound it above. D16 as recorded on 2026-09-24 asserted containment and was wrong | corrected here |
| **D23** | The runner's injection timestamp is a cached telemetry stamp, not a reading taken at the instant. It is `cached_vehicle_observation`, an open-above lower bound, carrying its `cache_age_host_s` | decided here |
| **D24** | No development run in this apparatus can produce a passing timing verdict, because the injection instant has no defensible upper bound. Discrete comparisons still decide, and an empty response window is still sound | decided here |
| **D20** | **Revised.** 0.352 s is the observed repeat-to-repeat range of one event over n=4 repeats. It is repeatability, not accuracy, and bounds nothing. "About 4.3 times the measured jitter" and "the safe direction" are withdrawn. 1.5 s stays for re-analysis under the criterion the runs were judged by | corrected here |
| **D21** | **Revised.** A statistic is formed over a cohort: valid runs, one composite identity including intended mode, one clock source. Gating on clock provenance alone let an invalid, differently configured run report 89 s of "jitter" | corrected here |
| **D14** | **Resolved: route (b), the repository's existing Ubuntu Actions.** A pinned `ubuntu-24.04` job with a 60-minute budget, ordinary permissions, no GPU and no privileged runner. Existing Linux CI shows the route is available, not that PX4 has ever built on it. No cloud instance is provisioned and the headless host is not rebooted | decided here |
| **D8** | Unchanged and explicitly pending. The C++ oracle needs no checker. Symbolic verification stays open; Python fixtures are not a model checker | recorded |
| **D17** | **Resolved by splitting, not by a new number.** U1 is the selector's response obligation after an eligible condition. U4 is commitment to an allowed navigation response. Landing, containment and completion are separate outcomes with their own observables. No speed-limit quotient is used as a deadline. Being already in an allowed response mode can satisfy a state obligation when its preconditions hold | decided here |
| **D7** | **Replaced.** A deterministic coverage gate, not a pooled binomial one. Every required cell needs a valid, observable, classified result, reported by mechanism, order and boundary. No population claim from a designed set of offsets. An unexplained discrepancy blocks claims for that subdomain | decided here |
| **D9** | **Replaced.** One supported pair first: neither, A only, B only, A then B, B then A, and one near-boundary schedule. Equal inputs must be realized and observed, not merely requested. A same-update cell is unavailable in SITL unless the apparatus can demonstrate that ordering | decided here |
| **D13** | Unchanged. RC stimulus stays out of integrated coverage. The native-class oracle may still exercise RC input flags; that is component evidence, not a MAVLink injection | recorded |
| **D25** | Scenario, execution and analysis identity are three separate records. A case cannot be selected by the hash of a readback that does not exist until launch | decided here |

The owner also corrected an overstatement of mine: the repair does not establish that no action is selected.
The supported statement is that no expected post-injection recovery-mode transition was observed and no new
failsafe announcement was seen, with the internal selected action and its cause unresolved.

## 2026-09-26 addendum — the oracle runs

**D14 is closed.** Route (b) worked. PX4 v1.17.0 at the pinned commit builds on an ordinary `ubuntu-24.04`
GitHub runner and its nine failsafe unit tests pass, each in its own process, from a hash-pinned binary. Nine
minutes wall clock against a 60-minute budget. No WSL, no cloud instance, no reboot of the headless host.
Evidence: [task-oracle-2026-09-26](../../../evidence/task-oracle-2026-09-26/README.md).

**The first dispatch was green and proved nothing.** ctest ran the gtest binary as one entry, suppressed its
output, and reported `Passed 0.00 sec`. No case name appeared in the log. The check now asserts the binary
lists as many cases as the source declares and runs each in its own process. A green job that cannot say what
it ran is worse than a red one, because it is quotable.

| id | decision | status |
|---|---|---|
| **D14** | Closed: the repository's own Ubuntu Actions, run manually, at a recorded toolchain identity | **resolved and executed** |
| **D26** | PX4's own suite passing is NOT a differential result. `Q-RECHARGE` and `Q-DELAY-EPS` stay transcription-checked until the model's own sequences are driven through this binary | decided here |

What this changes about the open question: the selector logic passes its own tests, so the integration is now
the more likely location of the fault than the selector. That is where to look next, not a diagnosis. The
supported statement is unchanged: no expected post-injection recovery-mode transition was observed and no new
failsafe announcement was seen; the internal selected action and its cause remain unresolved.

## 2026-09-29 addendum — the first differential, and a bug it found

Layer A (the Python model) was compared against layer B (PX4's real `Failsafe` class) on identical sequences,
using an adapter that constructs the class PX4 ships and calls `update()` as commander does. Evidence:
[task-differential-2026-09-29](../../../evidence/task-differential-2026-09-29/README.md).

**The first run found a defect in the model.** Seven of nine sequences agreed exactly. The two
clear-and-re-raise sequences disagreed by exactly one update period, at both 100 ms and 10 ms, so the gap scaled
with the step. The cause, which I had read off `update()` before seeing the result: the model fed
`updateStartDelay` the previous update's delayed status where the source passes the current one, and seeded a new
delay before the elapsed time was taken off. Corrected to the source's order, with integer microseconds.

**A claim of mine is retracted.** I wrote, beside the model and in a study guide, that the discrete stepper
"lands one update late" and that the real framework "has the same dependence on its own update period." It does
not. That figure was the bug. The corrected model gives exactly 2.5 s at every step size.

| id | decision | status |
|---|---|---|
| **D27** | The model follows `FailsafeBase::update()`'s own order and uses integer microseconds. Float seconds made the first RTL land at 5.0 or 5.1 s by rounding luck | decided here |
| **D28** | D26 is partly discharged. On the selected-action timeline, model and real class agree exactly on 11 sequences. The pot's value is private to the class and was not read, and the integrated runtime is layer C, still untested | recorded |
| **D29** | The differential agreeing means the SELECTOR is not where the missing recovery lives, on the domain these sequences cover: no mode-requirement fallback, no takeover, no deferral, one vehicle type. It does not localise the anomaly, and it does not say the integration is at fault | recorded |

## 2026-09-29 addendum — runtime diagnosis

**D30.** The reproduced Auto Loiter datalink-loss anomaly is localized to the
harness's integer parameter encoding and readback. The live selector consumed
an invalid integer action setting and returned `None`; corrected bytewise
transport restored Hold then RTL. The response also occurred on the original
uninstrumented executable. NP-8 is closed for this domain.

[The executed packet](../../../evidence/task-runtime-2026-09-29/README.md) records
the mechanism and limits; its [results JSON](../../../evidence/task-runtime-2026-09-29/results.json)
is the canonical home for measurements. This updates the unresolved inference
in D29 without altering the historical captures or declaring Study A complete.
Injection timing remains uncalibrated; a complete conformance campaign and the
matched interaction pilot still require their declared gates.

## 2026-09-30 addendum — owner sign-off

The owner delegated these decisions on 2026-09-30 ("make a decision for the
other repos"). They were made by Claude on the owner's behalf and are recorded
as the owner's decisions.

| id | decision |
| --- | --- |
| D1–D6, D10, D12 | Approved as built. D12's horizon stands; its timing tolerance is not a gate for confirmation runs until the injection instant is bounded (D24) and a tolerance is calibrated in advance (NP-6) |
| D7 | Approved **as replaced on 2026-09-25**: a deterministic coverage gate. Every required cell needs a valid, observable, classified result, reported by mechanism, order and boundary; an unexplained discrepancy blocks claims for that subdomain; no population claim from a designed set of offsets. The original count rule (≤3 of 60) is not used |
| D8 | Option (b): build the model and its queries, and defer checking. No checker is needed for Study A. Revisit UPPAAL's academic licence only if Study A passes and composition properties are next |
| D9 | Approved **as replaced on 2026-09-25**: one supported pair first (neither, A only, B only, A then B, B then A, one near-boundary schedule) |
| D11 | Approved: setpoint-only loss stays deferred until a ROS 2 offboard path exists |
| D13 | Accept five injectable event classes. No RC source is funded; RC loss stays component evidence through the native-class oracle |

Consequence for Study A: the [protocol](study-a-protocol.md) gains a matching
dated amendment (§7b) before any confirmation run.


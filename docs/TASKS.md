# UAV Recovery Contracts — long-term research backlog

This is the long-term backlog. The current plan and finish line are in
[ROADMAP.md](../ROADMAP.md); task status for the older 2026-09-05 sprint is in
[SPRINT_TASKS.csv](SPRINT_TASKS.csv).

> **Objective.** Produce the strongest, most honestly packaged evidence—not a completed
> fleet. Priority flows from leverage, falsifiability, and executability. It does not flow
> from the project's most ambitious possible demonstration.

Informed by a [source-reviewed directed dependency audit](research-dependency-audit.md) of
commit `a43d9e1`. Graphify supplied candidate relationships; only manually verified research
dependencies were retained. Repository navigation, CI, schemas, generated tasks, and raw
centrality counts are excluded from the published map. Novelty remains unresolved until URC-01
closes. No dates or estimates appear, by design.

## Formal-composition programme (proposed 2026-09-16)

A [formal-composition plan set](specs/formal-composition/README.md) proposes making formal composition of PX4 failsafes (timed-automata model, reachability, SITL witness replay) the thesis spine, with the empirical recovery-contract work below as its measurement layer and fallback. It is proposed only: no task, tier, gate or claim below changes until the owner merges it and a follow-up PR reconciles this backlog, the roadmap and the claim ledger.

## Two finish lines

The finish line now lives in [ROADMAP.md](../ROADMAP.md): PX4 only, Study A.
The two lines below predate that and still name ArduPilot.

**Ceiling.** Configuration-specific recovery contracts retain their registered coverage in
SITL, HITL, and contained single-vehicle tests; offline fleet composition shows lower mission
cost than one global envelope; a limited two-vehicle demonstration agrees with the registered
prediction.

**Floor.** A citable, pinned PX4–ArduPilot SITL conformance benchmark with held-out recovery-
tube coverage and an honest global-versus-individual comparison. A null result—one global
envelope is sufficient—is a completed floor, not a failed project.

The floor is the finish line this repository can reach without flight hardware or a facility.
Hardware work remains visible but cannot outrank executable software evidence.

_15 long-term project tasks · 8 Tier 0 · readiness requires completed predecessors._

**Gate types.** `preregister` — commit a decision before the data it judges; `external` —
requires a person, facility, or resource outside this repository; `build` — new implementation
or analysis; `hygiene` — reproducibility, search, or packaging debt.

**Tiers.** 0 finish · 1 package · 2 park. A task whose required resource or positive result is
not secured cannot be Tier 0, however impressive its eventual output might be.

---

## Tier 0 — finish

### URC-01 · Close the exact-gap and tooling search

2026-09-08: [URC-D01 first-pass review](prior-art-search-2026-09-08.md) is complete.
Full-text/tooling inspection and the documented broader-search shortfall remain;
URC-01 is not silently closed and no downstream gate is automatically promoted.

2026-09-15: [URC-01 decision](prior-art.md#urc-01-decision--2026-09-15-replacement-plan) recorded under the
replacement plan: evidence conclusion = prior art found on the reconnection and liveness axes (documentation),
no conclusion on equivalent intent and coverage (17 intake rows unread); gate status **partial**. URC-01 stays open.

`hygiene` · executable now

**Why it matters.** The source map proves that generic failsafes, cross-stack testing,
capability-aware safety, health contracts, contingency trajectories, and spatial reservations
already exist. It does not yet prove that configuration-specific native recovery traces and
reconnection semantics remain distinctive.

**What it adds.** A dated, reproducible boundary around the only claim this project can own.

**Done when.** `docs/prior-art.md` carries database and patent search strings, inclusion and
exclusion criteria, a source table for equivalent-intent PX4/ArduPilot benchmarks and failsafe-
configuration compilers, and a conclusion written as “supported candidate gap” or “prior art
found”—never “no one has done this.”

### URC-02 · Pin the configured-vehicle matrix and equivalent recovery intentions

`preregister` · executable now · after URC-01

**Why it matters.** “PX4 versus ArduPilot” is not an experiment. Without pinned firmware,
vehicle dynamics, full parameters, and an equivalence rule for Hold, Land, and RTL, any
difference can be explained after the fact as a configuration mismatch.

**What it adds.** Stable experimental identities and a defensible cross-stack comparison.

**Done when.** One committed matrix names both firmware identifiers, simulator and vehicle
model, complete parameter exports, recovery intentions, equivalence rules, unsupported cases,
and configuration hashes; the example manifest validates against the resulting contract.

### URC-03 · Freeze authority-loss, logging, and coordinate semantics

`preregister` · executable now · after URC-02

**Why it matters.** Setpoint timeout, process termination, mode transition, recovery completion,
and reconnection are currently prose concepts. A timestamp or coordinate-frame disagreement
would make trace alignment and tube coverage uninterpretable.

**What it adds.** One event vocabulary and one analysis-ready trace schema across both stacks.

**Done when.** A committed protocol defines the last valid setpoint, authority-loss timestamp,
native-transition timestamp, terminal state, reconnect event, sampling and clock rules,
coordinate transform, units, missing-data behavior, and invalid-run policy—with schema tests for
one valid and multiple invalid fixtures.

### URC-04 · Build the deterministic cross-stack SITL harness

`build` · executable now · after URC-02, URC-03

**Why it matters.** The repository currently has a protocol but no mechanism that can produce a
trace. Manual simulator operation would introduce different command histories and termination
timing across stacks.

**What it adds.** The first executable research apparatus: the same registered scenario can be
run against both configured vehicles.

**Done when.** One command launches each pinned stack, applies the registered pre-failure
setpoints, triggers both authority-loss mechanisms, records the required channels, saves a
manifest beside every log, and reproduces an identical no-fault control trajectory from a fixed
seed.

### URC-05 · Implement trace normalization and conformance checks

`build` · executable now · after URC-04

**Why it matters.** Native logs use platform-specific modes, fields, clocks, and frames. A model
cannot compare or cover traces until that variation is normalized without erasing real semantic
differences.

**What it adds.** A common authority automaton and auditable path from raw logs to comparison
tables.

**Done when.** Tested code maps raw traces into the frozen schema, preserves original mode
labels, emits normalized authority states, rejects incomplete provenance, detects impossible
transition order, and passes positive and negative synthetic fixtures for both stacks.

### URC-06 · Execute the pilot and estimate variability

`build` · executable now · after URC-05

**Why it matters.** The current 5%, 10%, and 20% values are engineering gates, not empirically
justified scientific thresholds. Confirmatory sample size and tube calibration cannot be frozen
until run-to-run variability and invalid-run frequency are known.

**What it adds.** The variance, failure modes, and effect scale needed to design a confirmatory
test without tuning it on the final data.

**Done when.** A balanced pilot covers both stacks and all valid recovery intentions, raw and
normalized traces retain full provenance, invalid runs are accounted for, and a pilot report
quantifies transition latency, braking response, envelope volume, missingness, and seed
sensitivity without calling the pilot held-out evidence.

### URC-07 · Freeze the confirmatory contract before generating validation traces

`preregister` · executable now · after URC-06

**Why it matters.** Choosing the coverage target, horizon, tube construction, volume
integration, split, or practical effect threshold after viewing confirmation data would turn the
main result into a post-hoc description.

**What it adds.** A result that can reject individualized recovery contracts rather than merely
fit them.

**Done when.** A dated commit fixes the calibration and held-out identities, random seeds,
sample unit, tube method, target and interval for coverage, horizon, coordinate frame,
integrated-volume calculation, global-envelope baseline, practical-effect rule, abstention rule,
and missing/invalid-run treatment; no confirmatory trace exists in the repository at that commit.

### URC-08 · Run the held-out contract test and take the registered branch

`build` · executable now · after URC-07

**Why it matters.** This is the project's decisive question. Fleet algorithms are unjustified
until individualized tubes retain coverage and save meaningful volume outside their calibration
set.

**What it adds.** Either evidence for configuration-specific contracts or evidence that the
simpler global envelope wins.

**Done when.** The frozen pipeline reports held-out full-trajectory coverage with uncertainty,
integrated reserved volume at matched coverage, transition and reconnection findings, and every
registered sensitivity; the decision log records positive, null, or conformance-failure outcome
without moving a gate.

---

## Tier 1 — package

### URC-09 · Release the versioned conformance benchmark

`build` · executable now · after URC-08

**Why it matters.** Whether individualized tubes win or lose, the pinned configurations, event
semantics, and trace corpus are independently useful. Leaving them as an internal experiment
throws away the project's most robust contribution.

**What it adds.** A citable artifact that survives a null fleet-allocation result.

**Done when.** A release contains configuration manifests, normalized traces or a documented
external archive, schemas, checksums, environment lockfiles, reproduction commands, data
dictionary, license, limitations, and the exact code commit used for the reported analysis.

### URC-10 · Compare offline fleet composition only if individualization passes

`build` · **blocked-on-positive-gate** · after URC-08

**Why it matters.** Neighbor evacuation is the system-level idea, but implementing it before
the single-vehicle contract proves useful would optimize a premise that may be false.

**What it adds.** A controlled comparison of native recovery, one global tube,
configuration-specific tubes, and configuration-specific tubes with cooperative evacuation.

**Done when.** Paired encounter scenarios replay held-out native traces; all methods use the
same failures and task weights; coverage, minimum margin, integrated reservation, and mission
cost are reported together; an oracle appears only as a bound.

### URC-11 · Write the positive-or-null research package

`build` · executable now · after URC-08, URC-09

**Why it matters.** A code and data release does not explain the novelty boundary, estimand,
negative result, or operational meaning to a research reviewer.

**What it adds.** The floor: a paper-style report and portfolio case study that remain honest
under every registered branch.

**Done when.** The package states the configured-vehicle unit, prior-art exclusions, protocol,
pilot/confirmation separation, effect sizes and uncertainty, failure branch, and evidence state;
every number and figure links to a committed generator and input.

---

## Tier 2 — park

### URC-12 · Secure an advisor, hardware path, facility, and safety ownership

`external` · **blocked-on-lab-access** · after URC-08

**Why it matters.** HITL and flight evidence require equipment, contained space, risk ownership,
and experienced review that this repository cannot grant itself.

**What it adds.** Legitimate authority and resources for leaving simulation.

**Done when.** A named advisor or responsible operator approves the hardware matrix, contained
test location, risk assessment, independent kill path, roles, stop conditions, and data-
ownership/publication terms in writing.

### URC-13 · Replicate the decisive result in HITL

`build` · **blocked-on-hardware** · after URC-08, URC-12

**Why it matters.** SITL timing does not establish flight-controller timing, scheduler jitter,
or real I/O behavior.

**What it adds.** A hardware-timing boundary on the recovery contract without yet exposing a
vehicle to flight risk.

**Done when.** Both pinned stacks run on documented flight controllers, decisive pilot and
held-out cases are repeated under the frozen semantics, timing distributions and conformance are
reported, and the SITL conclusion is retained or explicitly revised.

### URC-14 · Run contained single-airframe validation

`external` · **blocked-on-facility** · after URC-12, URC-13

**Why it matters.** A recovery tube becomes physical evidence only when native vehicle motion
is observed under an approved operating envelope.

**What it adds.** The first measured trajectory comparison, with airframe variation controlled
by flashing one matched vehicle alternately before using a second vehicle for external validity.

**Done when.** Approved tests capture Hold and Land before any RTL condition, every run has a
complete manifest and synchronized external reference, registered margins are scored without
gate changes, and anomalies remain in the dataset.

### URC-15 · Attempt a two-vehicle composition demonstration

`build` · **blocked-on-positive-gate-and-facility** · after URC-10, URC-14

**Why it matters.** The ceiling claim concerns composition, not two isolated recovery traces.
The demonstration has no value until both the offline algorithm and contained single-vehicle
contract are credible.

**What it adds.** A bounded physical example of one vehicle entering native recovery while a
cooperative neighbor exits its reserved space-time tube.

**Done when.** A preregistered, low-speed, contained scenario runs under independent safety
oversight; video, onboard logs, external tracking, minimum margin, and contract-conformance
verdict are committed; no claim extends beyond that tested envelope.

---

## Cross-cutting

These tasks are not included in the 15 project-task count.

### XC-01 · Reconcile the repository, portfolio, resume, and any paper abstract

`hygiene` · executable later · after URC-08

**Why it matters.** A null result or changed threshold must propagate to every public surface.
Conflicting claims look like carelessness rather than scientific iteration.

**What it adds.** One evidence state and one set of headline findings everywhere a reviewer can
encounter the project.

**Done when.** Every public claim and number traces to the same committed artifact and evidence
label, and all planned-only language is replaced only when the corresponding evidence exists.

### XC-02 · Record the publication and disclosure path before adding implementation-sensitive detail

`external` · executable now · before implementation-sensitive public disclosure

**Why it matters.** This repository is public. A website publication can affect patent options,
especially outside the United States, while ownership and disclosure obligations can depend on
where and how future work is performed. Making a repository private later does not erase an
earlier public disclosure.

**What it adds.** A deliberate public-first, publication-first, or counsel-reviewed path instead
of letting repository activity make the decision accidentally.

**Done when.** The owner records the repository's first-public date and either records that no
patent review is being pursued or consults the appropriate university technology-transfer office
or qualified counsel before adding potentially enabling control, hardware, or configuration
detail. This task is a process gate, not legal advice.

## Outstanding from the number-provenance audit (2026-09-25)

Ordered by how much each resolves. Ids resolve in [`protocols/quantities.json`](../protocols/quantities.json);
the gaps are tabulated in [the audit](number-provenance-audit-2026-09-25.md).

| # | task | resolves | how | depends on |
|---|---|---|---|---|
| NP-1 | ~~Run the native failsafe oracle once~~ **done 2026-09-26**: it builds and 9/9 cases pass ([evidence](../evidence/task-oracle-2026-09-26/README.md)). It closed the ENVIRONMENT question only | the environment question behind D14 | done | — |
| NP-1b | ~~Drive the shared-delay sequences through the oracle binary~~ **done 2026-09-29**: 11 sequences, exact agreement after one model defect was found and fixed ([evidence](../evidence/task-differential-2026-09-29/README.md)) | `Q-RECHARGE` and `Q-DELAY-EPS` are differentially checked | done | — |
| NP-8 | **Done for the reproduced Auto Loiter datalink case:** internal inputs, selector output and committed mode recorded; incorrect integer parameter transport identified and repaired | the reproduced missing-recovery cause | [Executed before/after packet](../evidence/task-runtime-2026-09-29/README.md); measured values in its results JSON | broader conformance remains open |
| NP-2 | Bound or abandon `Q-RESIDUAL` | U1 and U4 timing become evaluable, or are declared permanently unevaluable in this apparatus | instrument the runtime at the update boundary for a post-event acknowledgment with stated timestamp semantics, or state a defensible transport bound | NP-1 |
| NP-3 | **Source traced; runtime blocked.** Heartbeat aging/publication precedes commander's timeout; the new instrumented executable fails tracking | T1, T2 and T5 predictions | [Source trace, observed limits and retained attempts](../evidence/task-timing-2026-10-03/README.md); diagnose the instrumented runtime before measuring the complete chain | usable instrumented runtime |
| NP-4 | **Done for the new attempts:** full compiled registry read with types, including unused parameters | complete snapshot hash linked to execution artifacts; override hash retains its narrower scope | [Prospective criteria and executed captures](../evidence/task-timing-2026-10-03/README.md) | done |
| NP-5 | Validate `Q-HORIZON` against a recovery that actually happens | the horizon stops being a partial validation | any run that produces a recovery transition bounds it from below | a working stimulus |
| NP-6 | **No replacement tolerance calibrated.** Prospective diagnostic executed; host cessation remains unbounded above on the vehicle clock | timing remains outside pass/fail under signed protocol section 7b | [Executed outcome and conditional calibration design](../evidence/task-timing-2026-10-03/README.md); historical tolerances unchanged | NP-2 and usable instrumented runtime |
| NP-7 | Resolve the four literature rows with no intent disposition | closes the intent audit completely | L06 needs an identifier; L18, L42 and L50 need their abstracts | none |

None of these is blocked on an owner decision. NP-1 needs one workflow dispatch.

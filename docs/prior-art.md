# Prior-Art Boundary

## Current PX4 comparison

The scoped Python model and native differential are infrastructure. Agreement
with the implementation checks correspondence; mission safety needs an
independently specified requirement and the relevant outcome evidence.
Study A is [paused](../ROADMAP.md#disposition-and-finish-line), with D7 retained for any
resumption or claim based on that model. These contrasts describe the preserved
failsafe study. The separate [adopted software question](decision-log.md#2026-10-06-adopt-the-control-prototype-deployment-investigation)
has its numerical evidence in the [published successor](https://github.com/500ft/control-code-verification). No new mission-requirement
or firmware-migration result is claimed here.

The following primary-source passages were inspected for this reconciliation.
The contrast column describes this repository's executed scope, not an absence
claim about the rest of the literature.

| Source and inspected passage | Established work | Contrast with this repository's result |
| --- | --- | --- |
| [PX4 failsafe simulator](https://docs.px4.io/main/en/config/safety_simulation), description and usage | Runs the vehicle's failsafe code in a browser, tracks current code and includes configured delays | Our [native comparison](../evidence/task-domain-2026-10-03/README.md) pins the source and checks a separate Python implementation on declared sequences. Executing failsafe logic itself is existing tooling |
| [SaFUZZ, arXiv v1](https://arxiv.org/html/2601.05449v1), abstract and introduction | State-aware testing of transitions, failsafes and operator interactions under timing and environmental changes; simulation results checked in field tests | Our current evidence is component comparison and local SIH qualification, with public-log reconstruction separately excluded from replay. Cross-layer failsafe testing is established |
| [Nyctea, author-posted paper](https://lijuanru.com/publications/tosem25.pdf), introduction and §3–4 | Detects flight-state deviation and uses a learned agent to change control parameters during flight | Our executed work checks failsafe selection correspondence and observation. It performs no online configuration repair; configuration correction is established prior work |
| [Wang et al., ESEC/FSE 2021](https://yuleisui.github.io/publications/fse21.pdf), abstract and introduction | Classifies bugs, root causes and repair patterns from PX4 and ArduPilot histories | Our minimized adapter/model counterexamples concern a declared input domain. They are not a census of deployed configuration violations or a new general autopilot-bug taxonomy |

This targeted source cross-check adds no experiment or novelty verdict. It does
not close the historical unread-source or formal-axis review below. The dated
sections preserve the earlier fleet/envelope question and its superseded
conclusions; they do not replace the current roadmap.

## 2026-09-08 source review

[Dated exact-gap/tooling review](prior-art-search-2026-09-08.md) records executed
queries, 12 selected primary entries, overlap judgments and access limitations.
Prior art is confirmed for broad ingredients; the narrow dataset contribution
remains a supported candidate gap within this retrieval, not established novelty.
URC-D01 completes this first pass; full URC-01 closeout remains pending.
The most consequential protocol correction is to distinguish setpoint loss,
GCS-heartbeat loss and process termination before pinning equivalent intentions.

This is a scoped source map, not a claim of an exhaustive systematic review. Sources are included to define what this project must **not** claim as new.

## Established ingredients

| Area | Source | What it establishes for this project |
| --- | --- | --- |
| Configurable PX4 failsafes | [PX4 Safety / Failsafes](https://docs.px4.io/main/en/config/safety) | Failsafe actions and delays depend on configuration; “PX4 behavior” is not a single intrinsic response. |
| Configurable ArduPilot failsafes | [ArduPilot GCS Failsafe](https://ardupilot.org/copter/docs/gcs-failsafe.html) | Recovery action and mode behavior are parameter- and state-dependent. |
| Failure-injection tooling | [PX4 Failure Injection](https://docs.px4.io/main/en/debug/failure_injection) | Simulation and hardware fault injection are existing capabilities, not a contribution by themselves. |
| Cross-stack behavioral checking | [Avis](https://arxiv.org/abs/2106.14959) | PX4 and ArduPilot have already been subjected to in-situ model checking and bug discovery. |
| Capability-aware safety filtering | [CA-HCBF](https://arxiv.org/abs/2604.13245) | Generic capability-aware heterogeneous barrier functions cannot be a headline novelty claim. |
| Health contracts and reallocation | [Fail-operational swarm architecture](https://arxiv.org/abs/2608.20906) | Safety monitors, contracts, health vectors, and reallocation have already been combined architecturally. |
| Protected contingency trajectory | [Plan-and-Avoid](https://arxiv.org/abs/2608.06648) | Moving cooperative traffic away from a vehicle's contingency path is closely related prior work. |
| Dynamic spatial reservations | [Dynamic air corridors](https://doi.org/10.1016/j.robot.2026.105359) | Space-time corridor reservation under communication loss is not new in general. |
| Operational RTL hazard | [ATSB AO-2023-033](https://www.atsb.gov.au/investigations/ao-2023-033) | A large-drone-operation investigation provides motivation for composing recovery behavior before coordination is lost. |

<a id="candidate-gap"></a>

## Historical candidate gap

The earlier fleet/envelope proposal used this candidate gap:

> Physical and simulated composition of empirically calibrated native recovery traces from completely configured autopilot systems after companion-level command authority is lost, including mode transitions and reconnection behavior.

This is a **candidate distinctiveness claim**, not proof of global novelty. It must be checked again before submission against new publications, dissertations, standards, and patents.

## Claims explicitly excluded

This repository will not claim invention of:

- UAV failsafes or fault injection
- Collision avoidance or control barrier functions
- Contingency trajectories or spatial reservations
- Health-aware fleet reallocation
- Cross-autopilot testing
- Return-to-launch coordination as a general problem

## Search questions still open

- Has an existing benchmark already mapped equivalent failsafe intentions across pinned PX4 and ArduPilot configurations?
- Has a parameter compiler translated an abstract recovery contract into both stacks and verified trace conformance?
- Has post-companion-loss reconnection behavior been included in empirical fleet recovery tubes?
- Which standards define evidence expectations for operational contingency-volume coverage?

Answers to these questions must be added with dated search strings and primary sources before the novelty statement is frozen.

## URC-01 closeout — 2026-09-15

**Superseded the same day** by the [URC-01 decision under the replacement plan](#urc-01-decision--2026-09-15-replacement-plan) below. The executed-query table and the criteria in this section stand; its source table, axis summary and conclusion do not: the clarified axis definitions changed 18 judgments and the full intake screen exposed 17 unread candidates.

This section meets the URC-01 done-when in [TASKS.md](https://github.com/500ft/uav-failsafe-composition/blob/cdb7b36d01085527529fde3bead4543c1e038e43/docs/TASKS.md#urc-01--close-the-exact-gap-and-tooling-search):
search strings, inclusion/exclusion criteria, a source table, and a conclusion in one of the two allowed forms.
It is bounded by the inspected set below. It is not an exhaustive systematic review.

### Database search strings actually executed

Canonical export: `evidence/task-2026-09-11-public/database-export.json` (provenance-clean, 317 identifier
records, retrieved 2026-09-11T21:25:39Z). Every leg is reproduced from its query log, not retyped:

| database | query | status | n |
|---|---|---|---|
| crossref | `PX4 ArduPilot failsafe differential testing` | ok | 40 |
| openalex | `PX4 ArduPilot failsafe differential testing` | ok | 17 |
| crossref | `PX4 ArduPilot recovery benchmark` | ok | 40 |
| openalex | `PX4 ArduPilot recovery benchmark` | ok | 50 |
| crossref | `UAV autopilot failsafe configuration testing fuzzing` | ok | 40 |
| openalex | `UAV autopilot failsafe configuration testing fuzzing` | ok | 18 |
| crossref | `UAV communication loss contingency recovery contract` | ok | 40 |
| openalex | `UAV communication loss contingency recovery contract` | ok | 50 |
| crossref | `multicopter failsafe behaviour conformance testing simulation` | ok | 40 |
| openalex | `multicopter failsafe behaviour conformance testing simulation` | ok | 2 |
| arxiv | `PX4 ArduPilot failsafe` | ok | 0 |
| arxiv | `PX4 ArduPilot testing` | ok | 5 |
| arxiv | `ArduPilot fuzzing` | ok | 2 |
| arxiv | `UAV failsafe recovery contingency` | ok | 0 |
| arxiv | `multicopter autopilot conformance testing simulation` | ok | 0 |
| arxiv | `UAV communication loss contingency recovery` | ok | 0 |

Recall of this export against the eligible day-1 set is **3/6**
(`scripts/reference_coverage.py --check`). The 2026-09-09 export fails the native-response audit and is
credited for nothing. The day-1 web-index queries are listed in
[prior-art-search-2026-09-08.md](prior-art-search-2026-09-08.md). Successor screening on 2026-09-15 used
Crossref and OpenAlex by DOI only; no new search legs were added.

### Patent search

**Not searched.** No patent database route was reachable from this repository's tooling on 2026-09-09 or
2026-09-15 (Crossref, OpenAlex and arXiv are scholarly indexes and do not cover patents). One patent (U12) was
read as public text; that is technical overlap only, not legal clearance. A patent search is an open item,
not a closed one.

### Inclusion and exclusion criteria (as applied)

- Day-1 set: the 12 sources selected by the 2026-09-08 review, every one accounted for in
  `docs/source-eligibility-register.json` with an explicit reason.
- Eligible for database recall: a scholarly record with a resolvable DOI or arXiv id (6 of 12).
- Stated, not dropped, and never counted as recall: code repositories, vendor documentation pages, patents
  (6 of 12).
- Successors: any Crossref-surfaced 2026 work citing or extending PGFuzz whose title touches a novelty axis
  (3 found on 2026-09-12, all screened 2026-09-15). They are recorded as S-ids, not added to the day-1
  register.
- A source counts as inspected only when its full text (or repository tree) was opened and hashed.
  Abstract-only or unreachable sources stay `unresolved` on every axis.

### Source table: equivalent-intent PX4/ArduPilot benchmarks and failsafe-configuration tooling

Per-axis state from each reading record's `axis_states` (D = disclosed or addressed, N = not found in the
inspected sections, U = unresolved). Generated from `docs/day3-reading-records.json`.

| id | source | access | intent | reconnection | coverage | liveness/setpoint |
|---|---|---|---|---|---|---|
| U1 | Avis, 2021 v1 | `full_text_sections` | N | N | D | U |
| U2 | PGFuzz, NDSS 2021 | `full_text_pdf` | N | N | D | N |
| U3 | PGFuzz code | `repository_tree_and_source` | N | N | D | N |
| U4 | RouthSearch, 2025 v1 | `full_text_html` | n/a | N | D | N |
| U5 | aerial-autonomy-stack, 2026 v2 | `full_text_sections` | N | N | N | U |
| U6 | PX4 failsafe simulator | `official_documentation` | D | N | D | N |
| U7 | PX4 Offboard | `official_documentation` | D | N | U | U |
| U8 | ArduPilot GCS failsafe | `official_documentation` | U | D | U | U |
| U9 | ArduPilot Guided commands | `official_documentation` | N | N | D | D |
| U10 | Plan-and-Avoid, 2026 v1 | `full_text_html` | n/a | n/a | n/a | n/a |
| U11 | Fail-operational swarm architecture, 2026 v1 | `full_text_html` | D | N | N | D |
| U12 | EP3662460B1 | `patent_claims` | N | D | N | U |
| S1 | UAVConfigFuzzer: Detecting Incorrect Configurations in UAVs via Setpoint Estimation Guided Fuzzing (Registered Report), FUZZING Workshop 2026 | `full_text_pdf` | N | N | N | N |
| S2 | ADGFuzz: Assignment Dependency-Guided Fuzzing for Robotic Vehicles, NDSS 2026 | `full_text_pdf` | N | N | N | N |
| S3 | PGPatch: Policy-Guided Logic Bug Patching for Robotic Vehicles, IEEE S&P 2022 | `full_text_pdf` | N | N | N | N |

Axis summary (from `scripts/reference_coverage.py`):

| axis | status | disclosed by | not found in inspected sections of | unresolved for |
|---|---|---|---|---|
| `equivalent_intent` | **narrowed_by_disclosure** | U7, U6, U11 | U1, U5, U12, U2, U9, U3, S1, S2, S3 | — |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U11, U3, S1, S2, S3 | — |
| `coverage` | **narrowed_by_disclosure** | U1, U2, U4, U6, U9, U3 | U5, U12, U11, S1, S2, S3 | — |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U9, U11 | U2, U4, U6, U3, S1, S2, S3 | — |

### Conclusion

**Prior art found, per axis.** Taken one at a time, every axis is `narrowed_by_disclosure`: an inspected
source already discloses cross-configuration intent in contract form (U6, U7, U11), documents behaviour on
reconnection (U8, U12), measures a trajectory-distance coverage of some kind (U1, U2, U3, U4, U6, U9), and
separates liveness from setpoint loss (U9, U11). None of these can be a headline claim.

**Supported candidate gap, bounded by this inspected set**, for the composed claim only: no inspected source
fixes one recovery intention, pins two autopilot configurations that are supposed to realise it, injects
liveness loss and setpoint loss as distinct faults, records the command-return phase, and compares the
realised trajectories against a calibrated coverage measure. The three 2026 successors and the PGFuzz code
do not change this: S1 is PX4-only configuration fuzzing, S2 is ArduPilot-only assignment-bug fuzzing, S3
patches per-autopilot fail-safe formulas without comparing them, and U3's code carries two independent
policy lists.

Bounds on that sentence: no patent search; no dissertation or standards search; no source outside the 15
inspected; recall of the canonical export is 3/6 against a 6-source anchor set, so the database leg is known
to miss relevant work. This closes URC-01 as a *dated boundary*, not as a novelty verdict. It does not close
URC-S08 or any owner gate. It must be re-run before any submission.

## URC-01 decision — 2026-09-15 (replacement plan)

Written against the URC-01 done-when in [TASKS.md](https://github.com/500ft/uav-failsafe-composition/blob/cdb7b36d01085527529fde3bead4543c1e038e43/docs/TASKS.md#urc-01--close-the-exact-gap-and-tooling-search),
clause by clause, under [docs/specs/prior-art-closeout/plan.md](specs/prior-art-closeout/plan.md). Evidence:
[execution README](../evidence/task-prior-art-closeout-2026-09-15/README.md),
[sources.json](../evidence/task-prior-art-closeout-2026-09-15/sources.json).

### Search history, by kind (clause: search strings)

- **Web-index discovery, 2026-09-08** (six strings, verbatim in
  [prior-art-search-2026-09-08.md](prior-art-search-2026-09-08.md) ("Exact executed strings")); three of them are
  patent-domain queries on Google Patents: strings 4–6. This is web discovery, not a native patent export.
- **Native scholarly exports, 2026-09-09 (rejected, audit-failed) and 2026-09-11 (canonical, 16 legs, 317
  rows)**: the executed (database, query, status, n) table is in the superseded section above and stands.
- **Identity lookups, 2026-09-15**: Crossref by DOI (S1, S2), Crossref bibliographic first-five (S3), OpenAlex
  and Semantic Scholar OA status (S3). Not discovery legs.
- **Technical disclosure reading of one patent** (U12, claims 1–3). Not legal review.
- **Not performed**: a native patent-database search campaign, dissertation and standards searches. Their
  absence is stated, not equated with a zero-hit search or with clearance.

### Relevance criteria and access limitations (clause: inclusion/exclusion)

Day-1 review criteria as frozen in the [rubric clarification](day3-reading-rubric.md#2026-09-15-clarification-plan-docsspecsprior-art-closeoutplanmd-t01):
include cross-autopilot execution, timed safety/configuration policies, communication-loss recovery,
trajectory reservations; exclude tutorials, anecdotes, throughput-only work, unrelated domains, marketing;
missing abstract or unclear relevance is unresolved. Separately, the day-1 reference denominator (U1–U12)
is fixed and byte-identical; register eligibility is a coverage rule, not a relevance rule. Access: full
texts for U1, U2, U4, S1, S2 and the three arXiv HTML sources; vendor pages for U6–U9; patent text for U12;
repository files for U3 (pinned commit); S3 from an author-posted copy because the publisher copy is
closed. Seventeen intake rows are metadata-only (C-ids) and unread.

### Comparator table (clause: source table)

Locators are the record's `locator`; per-axis rationales are in each record's `axes` text.

| id | identity / version | pinned configurations | equivalent-intent rule | loss stimulus | reconnection | coverage endpoint | code | locator |
|---|---|---|---|---|---|---|---|---|
| U1 | Avis, arXiv 2106.14959 v1 | PX4 and ArduPilot SITL, versions per paper | none (in-situ model checking vs profiling runs) | sensor-instance failures | not found | state-deviation invariant vs profiling runs, eq. (1) | yes (paper artifact) | Sections IV-C1/2, equations 1 and profiling-state definitions |
| U2 | PGFuzz, NDSS 2021 | ArduPilot, PX4, Paparazzi, per-autopilot policy sets | none (per-autopilot MTL policies) | commands, parameters, environment | not found | distance to one policy violation | yes (U3) | Abstract; Sec. I (fail-safe MTL example and distance metrics); Sec. III threat model (self-sabotaging inputs out of scop |
| U3 | PGFuzz code @7eaebf2 | separate ArduPilot/ and PX4/ trees | none (two hard-coded policy lists) | parameters/commands; heartbeat loss = crash oracle | not found | per-policy state error (update_distance.py) | yes, Python 2, read not run | README.md (Cases 1-2: parachute; PX4 GPS fail-safe COM_POS_FS_DELAY; Sec. 6 bitcode notes); ArduPilot/fuzzing.py L145-20 |
| U4 | RouthSearch, ISSTA 2025 / arXiv 2505.02357 | ArduPilot and PX4 PID configs | not applicable (PID specification inference) | PID values | not found | per-mode MTL oracle, eq. (8) | per paper | Abstract; Sec. 4.3 Misbehavior Validation (MTL oracle for ArduPilot RTL ascent); Sec. 5.1 Experimental Settings |
| U5 | aerial-autonomy-stack, arXiv 2602.07264 v2 | PX4 and ArduPilot via one ROS 2 interface | none (shared interface only) | none | not found | none (simulation throughput) | yes | Sections III and IV-A1/2/3 |
| U6 | PX4 safety_simulation docs | one PX4 parameter set at a time | none (action table for one config) | simulated failsafe triggers | not found | static action table | n/a (docs) | Whole page: embedded simulator description, note on COM_FAIL_ACT_T delay |
| U7 | PX4 Offboard docs | PX4 Offboard mode | none | proof-of-life stream (COM_OF_LOSS_T) vs setpoint topics, documented | not found | none | n/a (docs) | Description; ROS 2 Offboard Control |
| U8 | ArduPilot GCS failsafe docs | Copter FS_GCS_ENABLE / FS_OPTIONS | none | GCS heartbeat loss (FS_GCS_TIMEOUT) | documented: mode not restored on reconnect | none | n/a (docs) | When the failsafe will trigger; What will happen |
| U9 | ArduPilot Guided commands docs | Copter Guided | none | setpoint timeout (3 s stop) documented 09-12; sentence absent from today's page text | not found | none | n/a (docs) | Position/velocity target sections: 'should be re-sent every second (the vehicle will stop after 3 seconds if no command  |
| U10 | Plan-and-Avoid, arXiv 2608.06648 v1 | none (planner) | not applicable | not applicable | not applicable | not applicable | yes | Table of contents; Abstract; Sec. II-A Contingency Landing Planning; no occurrence of link/communication loss in the ful |
| U11 | Fail-operational swarm architecture, arXiv 2608.20906 v1 | one architecture | contract for one architecture, no equivalence | heartbeat/SNR only | not found | none (monitor coverage is a diagnostic metric) | no | Sec. III-C Formal Derivation of Safety Contracts, eq. (6) Communication Contract (heartbeat timestamp + SNR -> Return-To |
| U12 | EP3662460B1 | none (patent) | none | radio-link loss | disclosed: regain control after communication failure | none | n/a | Claims 1–3 |
| S1 | UAVConfigFuzzer, FUZZING 2026 | PX4 v1.15.0 only | none | configuration values only | not found | mission deviation / interruption oracles | not stated | Abstract; Sec. I; Sec. II-A (configuration parameters); Sec. III-A/B (three oracles: rapid ascent/descent, deviation, in |
| S2 | ADGFuzz, NDSS 2026 | ArduPilot Copter/Plane/Rover SITL | none | parameters/commands; heartbeat loss = crash oracle | not found | code/MIS coverage; 7 s drift oracle | not stated | Abstract; Sec. I; Sec. III-C threat model (GCS spoofing / link hijacking named as attacker tactics, out of the bug class |
| S3 | PGPatch, IEEE S&P 2022 | ArduPilot, PX4, Paparazzi (per-autopilot formulas) | none (per-autopilot PPL fail-safe formulas) | none injected; failsafe_gcs_check only a code-map entry | not found | patch completeness/performance | not stated | Abstract; Sec. I (PX4 GPS fail-safe / COM_POS_FS_DELAY example); Sec. II/III (PPL formulas: PX4 GPS fail-safe, ArduPilot |

Unread candidates from the full intake screen (metadata only, all axes unresolved): C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 —
see the [reconciled coverage section](reference-coverage-2026-09-12.md#2026-09-15-reconciled--current-axis-table-under-the-replacement-plan-urc-r03).

Axis summary (script output):

| axis | status | disclosed by | not found in inspected sections of | not applicable | unresolved for |
|---|---|---|---|---|---|
| `equivalent_intent` | **supported_bounded** | — | U1, U5, U7, U8, U12, U2, U6, U9, U11, U3, S1, S2, S3 | U4, U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `reconnection` | **narrowed_by_disclosure** | U8, U12 | U1, U5, U7, U2, U4, U6, U9, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `coverage` | **supported_bounded** | — | U1, U5, U7, U8, U12, U2, U4, U6, U9, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |
| `liveness_vs_setpoint_injection` | **narrowed_by_disclosure** | U7, U9 | U1, U5, U8, U12, U2, U4, U6, U11, U3, S1, S2, S3 | U10 | C001, C087, C158, C180, C186, C214, C228, C004, C005, C021, C135, C166, C182, C218, C219, C225, C266 |

### Evidence conclusion (clause: conclusion in an allowed form)

- `reconnection`: **prior art found.** Documented behaviour exists (U8: mode is not restored when the GCS
  heartbeat returns; U12: regaining control after communication failure is claimed). The claim to remove is
  "reconnection behaviour is unstudied"; what may remain is a *measured cross-configuration comparison*
  of the command-return phase, which no inspected source performs.
- `liveness_vs_setpoint_injection`: **prior art found.** The distinction is vendor-documented as a
  specification (U7: proof-of-life stream and timeout separate from setpoint topics; U9 as read on
  2026-09-12: separate Guided setpoint timeout). The claim to remove is "the distinction is unrecognised";
  what may remain is *injecting the two losses as distinct stimuli* and comparing realised behaviour.
- `equivalent_intent` and `coverage`: **no conclusion.** No inspected source discloses either axis under the
  clarified definitions (13 and 14 `not_found_in_inspected`, none disclosed), but 17 relevant or
  ambiguous intake rows are unread, and at least C001, C180, C004, C005, C135 could bear on equivalent intent
  across autopilots. Unread sources cannot support a gap. A "supported candidate gap" sentence is therefore
  **not** written for the composed claim today.

No sentence in this document says that no one has done this.

### Gate status: **partial**

Met: executed database and patent-domain web strings recorded with provenance; criteria stated; comparator
table covers every U/S source; conclusion written only in allowed forms.
Unmet, with next bounded work:

1. Full-text reading of the 7 `needs_full_text` rows (C001, C087, C158, C180, C186, C214, C228), starting with
   C001 and C180 (axis-1 threats), then resolution of the 10 `unresolved_metadata` rows by abstract or
   full text (C004, C005, C021, C135, C166, C182, C218, C219, C225, C266).
2. Re-verification of U9's 3-second setpoint-timeout sentence against a current page or the ArduPilot
   source, since today's page text no longer contains it.
3. A native patent-database search and dissertation/standards searches remain absent; the owner decides
   whether URC-01 requires them before any disclosure (XC-02 applies).

URC-01 stays open. Nothing here promotes URC-S08, URC-02 or any experiment.

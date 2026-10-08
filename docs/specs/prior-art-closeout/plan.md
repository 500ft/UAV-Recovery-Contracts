# Prior-art review and conditional URC-01 closeout — implementation plan

Status: executed 2026-09-15 on `task/prior-art-closeout-2026-09-15` (packet complete; URC-01 gate partial, see docs/prior-art.md). Sequence note (2026-09-15): PR #12 and its implementation PR #14 were merged into main before this replacement was reviewed; T00 must record that state, and the implementation reconciles #14's records, regenerated artifacts and closeout prose under this plan's rules rather than starting from the reviewed base. This plan supersedes [PR #12](https://github.com/500ft/uav-failsafe-composition/pull/12), reviewed at `96fb5a7069c83a0741ae813df0420339e3921f54`. This PR changes this document only. Merge the replacement plan before starting its implementation on a fresh task branch.

Prepared: 2026-09-14; revised 2026-09-15. Reviewed base: `2c72e0288129e9f50d5768189263cbf83136aa08` (main after PR #11). At implementation start, record the actual main/merged-plan commit and compare changes since this base; this SHA is review provenance, not permission to overwrite newer work. Use `task/prior-art-closeout-<actual-start-date>`, one implementation PR to main.

**Deliverable:** an auditable review of the retained discovery set, the three named follow-up sources, and U3, with reconciled findings and an evidence-based URC-01 decision. Completing this packet and closing URC-01 are separate outcomes. An access failure, relevant unread competitor, or contradictory finding may leave URC-01 open after the packet is delivered.

## Review of the original plan

| Problem in PR #12 | Required correction |
| --- | --- |
| Unresolved sources force a “supported candidate gap” conclusion; day acceptance nevertheless requires full closeout. | Let evidence determine the conclusion. Report gate status separately; unresolved evidence cannot supply support for a gap. |
| “No patent database run (none reachable)” is asserted without a current attempt. | Preserve the three executed patent-domain web queries in the [day-1 report](../../prior-art-search-2026-09-08.md) and U12's inspected claims. Distinguish web discovery, native database exports, and legal review. Do not invent a failed route. |
| Register eligibility is reused as literature inclusion criteria. | Keep the fixed day-1 reference denominator separate from relevance screening. Vendor docs, code and patents can be relevant while ineligible for scholarly-export coverage. |
| New reading records are treated as sufficient to repair the axis table. | Reconcile existing contradictions first: U6/U9 say no trajectory coverage in prose but carry affirmative coverage states. Review U1/U2/U4's related metrics against the exact coverage definition too. Re-open source sections before changing judgments. |
| The scripts allegedly reject all invalid assessments and enforce unread-source rules. | `novelty_axes()` currently downgrades invalid states to unresolved, omits wholly missing axes, and does not gate on access. `build()` promotes `abstract_only` to assessment-available. Add small behavioral regressions and fix these existing consumers. |
| The 317-record canonical export remains unscreened while three named sources stand in for closeout. | Screen the complete retained metadata set under fixed relevance criteria; enumerate further relevant unread candidates instead of silently excluding them. |
| A hash and a generic locator are enough to call a paper fully inspected. | Record exact version, accessed sections, extraction method, full hashes, and retained local copies. Hashes identify bytes; they do not establish what was read. |
| Removing a record tests stale output only; T8 omits the presentation test command used in CI. | Test unsafe access promotion and missing axes as well as stale outputs, then run every existing CI command. |

The record's phrase “three 2026 successors” is not reliable metadata: it also labels PGPatch as S&P 2022. Call these **follow-up sources** until their identities and dates are verified. A title determines review priority, not a novelty judgment.

## Frozen procedure and scope

### Inputs, identities and acquisition boundary

- Keep U1–U12 as the original reference-set identities and leave `docs/source-eligibility-register.json` byte-identical. Their reading assessments may be corrected in T10. This preserves the scientific denominator, not just a test expectation. Do not change register aliases or repair old exports; verified identities for new readings remain separate metadata.
- Reserve `S1` = UAVConfigFuzzer (`10.14722/fuzzing.2026.23009`), `S2` = ADGFuzz (`10.14722/ndss.2026.231014`), `S3` = PGPatch (DOI to verify). Confirm title, authors, venue/year and version through publisher/primary metadata before assessing text. If an ID is already assigned to a different work, resolve the collision in the plan before writing records.
- Permit exact identifier/title lookups and primary-source opens for these named sources, U1–U12 corrections and U3. For PGPatch, start with a Crossref bibliographic lookup for `PGPatch`, first five results, then verify the matching publisher record; retain ambiguity if no unique match exists. This is identity resolution, not a new discovery leg.
- No new broad searches, database-export reruns or native patent-search campaign. Inventory existing executed queries and outcomes accurately. Read query strings and database/query pairings from the retained logs; the script's current `QUERIES` list alone does not prove execution.
- The canonical intake is `evidence/task-2026-09-11-public/database-export.json`: 317 normalized identifier records, 16 logged query legs at this base. Screen all retained records, not only the 22-row ranked subset. Preserve row indices and identifier aliases; do not call identifiers distinct studies. Source identity resolution does not change the reference denominator.
- Leave raw exports, existing candidate CSVs, historical logs and the day-1 report untouched. The two existing generated JSON artifacts may change through their generators. Their historical directory/route labels do not make a later read a September 9 acquisition; retain each real `retrieved_on` date and explain this legacy naming in the evidence README.

### Access and evidence contract

Use the [day-3 rubric](../../day3-reading-rubric.md), with the clarified axis meanings below. Retain the existing record fields: `source_id`, `title`, `url`, `access`, `version`, `text_sha256_prefix`, `locator`, `aboutness`, `evidence_grade`, `finding`, `axes`, `axis_states`, `retrieved_on`. U3 additionally records `commit_sha` and `files_inspected`. For each axis, its `axes` text must name the inspected section/file and explain the judgment; a source-wide locator alone cannot justify four different findings.

For unavailable or ambiguous sources, keep a record under its reserved ID using the actual attempted source/identity-lookup URL, explicitly unverified title/identity, null unknown version/hash/aboutness, an access explanation and four unresolved states. This preserves mandatory-source accounting without inventing a DOI or manufacturing inspected text. The existing generators require a string `url`; an actual attempted lookup route satisfies that requirement without being represented as a confirmed paper URL.

Inspected access values are exactly `full_text_sections`, `full_text_pdf`, `full_text_html`, `official_documentation`, `patent_claims`, `repository_files`. They describe the available text, not that every page was read. `metadata_only`, `abstract_only`, `inaccessible`, `not_reinspected`, missing access and unknown access values do not establish an inspected assessment. Preserve the exact access failure in evidence; do not treat all uninspected sources as unreachable. Attempt at most the primary route and one lawful publisher/author/archive alternative per missing text, with no paywall bypass, purchase or outreach. A failure of one route is not a finding that no copy exists.

Every record must expose all four axes. Allowed states remain `disclosed_or_addressed`, `not_found_in_inspected`, `not_applicable`, `unresolved`. Unknown/missing states, an empty locator, or uninspected access yield `unresolved` in the coverage consumer. Missing axes must appear explicitly unresolved. Tests reject invalid committed record states, duplicate source IDs and unknown axis names. Neither consumer may infer a state by substring matching the prose.

| Axis | What an affirmative finding must address |
| --- | --- |
| `equivalent_intent` | Equivalence of a stated recovery intention across identified configurations; sharing an interface or selecting one configured action is related work, not by itself this comparison. |
| `liveness_vs_setpoint_injection` | Separately identified liveness/heartbeat and setpoint-loss stimuli and their semantics; heartbeat loss alone does not establish the distinction. |
| `reconnection` | What happens to command acceptance/authority when the relevant input returns. Distinguish documented behavior from a measured comparison. |
| `coverage` | Calibrated whole-recovery-trajectory containment over a specified horizon with separate evaluation; code coverage, policy-distance scores, per-mode oracles and static action tables are not this endpoint. |

`disclosed_or_addressed` can describe a discussion or specification, not just an experiment, but its rationale must state which. `not_found_in_inspected` is a bounded reading result, never global absence. `not_applicable` needs a stated reason and is not positive gap support. Partial overlap remains in the prose and the competitor table even if it does not meet the exact affirmative definition. A surviving combination of existing ingredients is not automatically novel.

Store source snapshots outside Git under `~/.cache/uav-failsafe-composition/prior-art-closeout/<actual-start-date>/`. Commit a compact `evidence/task-prior-art-closeout-<actual-start-date>/sources.json` manifest containing source ID, requested/final URL, actual UTC date, version/commit, observed transport status or tool error, raw SHA-256, extracted-text SHA-256, extraction command/version, local snapshot location, inspected locators and availability. Use null plus a reason when bytes were unavailable; never hash an error page as paper text. For U3, hash each inspected file and pin the commit. Do not commit full copyrighted papers or credentials. Later byte changes are new acquisitions, not silent replacements.

### Relevance screen and conclusion rule

Use day-1's review inclusion criteria: cross-autopilot execution; timed safety/configuration policies; communication-loss recovery; trajectory reservations. Exclude ordinary tutorials, unsupported anecdotes, throughput-only work, unrelated domains and marketing. Missing abstracts or unclear relevance are unresolved, not exclusions. Conference prestige and ranking score are not screening criteria.

The new `candidate-screening.csv` in the execution evidence directory has one row per retained raw hit, preserving zero-based `raw_index`, `id`, `title`, `url`, `decision`, `reason`, `reading_source_id`, and `duplicate_of`. Decisions are `exclude_out_of_scope`, `duplicate_identifier`, `linked_inspected`, `needs_full_text`, `unresolved_metadata`. Exclusions name the criterion; exact alias duplicates point to the retained row/reading record and stay countable. `linked_inspected` requires identity agreement and an actual inspected reading record, not a title match. Every row gets a decision; the original candidate files remain unscreened historical inputs.

For relevant unread hits not already represented by U/S records, add metadata-only reading records with all four axes unresolved, using `C` plus the first retained row's one-based index padded to three digits (for example, first row → `C001`). Resolve exact DOI/arXiv aliases against known records before allocating an ID; uncertain duplicates remain separate. These additional records make the unresolved population visible in the generated axes. Their full-text reading is deferred and named, not an unbounded expansion of this packet. All 317 rows can be screened in small resumable batches; completion is based on accounted-for rows, not a one-day promise.

URC-01 has two independently reported fields:

1. **Evidence conclusion:** use `prior art found` when an inspected source supports overlap, identifying the exact claim to remove or narrow. Use `supported candidate gap` only for a precisely stated remaining claim supported by completed relevant reading and its bounded search scope. Unread sources cannot support either conclusion about their contents; unresolved competitors that could settle the remaining claim prevent a positive closeout decision. No forced conclusion sentence when evidence is insufficient.
2. **Gate status:** `complete`, `partial` or `blocked`, with unmet acceptance items and named next work. Check the actual [URC-01 done-when](https://github.com/500ft/uav-failsafe-composition/blob/cdb7b36d01085527529fde3bead4543c1e038e43/docs/TASKS.md#urc-01--close-the-exact-gap-and-tooling-search), source-review dependencies and claim scope. If more searches, full texts or applicable disclosure guidance are required, keep URC-01 open; this plan does not waive them. Do not change the backlog's two allowed conclusion forms or lower its gate to obtain a green status.

Report the retained patent-domain queries as **web-index discovery**, the native scholarly exports as such, and U12's inspected claims as technical disclosure reading. A new native patent search was not performed; do not equate that with no patent search history, a zero-hit search, or legal clearance. Registration eligibility and 3/6 known-reference coverage are not literature relevance or global recall. The rejected historical export receives zero credited hits because its audit fails, not because it successfully searched and found no anchors.

## Ordered execution tasks

Checkboxes track execution of this plan. The aggregate packet status belongs to `URC-R03` in [SPRINT_TASKS.csv](../../SPRINT_TASKS.csv); URC-01 remains a separate research gate. Source-reading tasks contain natural acquisition/section checkpoints; do not rush a paper to satisfy an arbitrary time estimate. No simulator, source-review or source-access result is asserted by an unchecked task.

### [x] T00 — Record the starting state

- Files: new execution evidence `README.md`; read main, this merged plan, `AGENTS.md`, CI, the rubric and current task ledger.
- Do: start an isolated clean checkout, record the base/merged-plan SHAs, branch, interpreter/dependency versions and input SHA-256s. Check U/S/C and `URC-R03` ID collisions. Run the baseline gate commands below.
- Done when: actual outputs and exits are retained. At the reviewed base there are 40 repository tests and 4 presentation tests; re-observe counts. The historical candidate evaluator is not a current gate; do not re-pin it to hide drift.

### [x] T01 — Commit the review contract before new reading

- Depends on: T00. Files: `docs/day3-reading-rubric.md`, execution evidence `README.md` and `sources.json` (new).
- Do: add a dated clarification of the four axes, access vocabulary, relevance criteria, identity map, acquisition limit and conclusion rule above. Preserve the original rubric as historical context. Freeze the canonical export hash, the expected 317-row intake and the baseline query/alias inventory. Use actual execution dates and disclose that this is a targeted follow-up after earlier results were known.
- Done when: the procedure commit precedes source retrieval and judgments; any input drift is explained before proceeding. This is not a blind or independent preregistration.

### [x] T02 — Reproduce access and missing-axis defects

- Depends on: T01. Files: `tests/test_acquisition_ledger.py`, `tests/test_reference_coverage.py`.
- Do: add focused fixtures for abstract-only/unknown access with an affirmative or negative state; an inspected source missing one/all axes; and an inspected source with a real locator. Assert that unread input cannot become assessment-available or support a gap, and missing axes remain visible as unresolved. Keep the existing bad-state/missing-locator regression, using a real axis instead of arbitrary `a`.
- Done when: the unsafe cases fail on the current consumers for the intended assertion, with failing output retained; no network calls or research assertions enter tests.

### [x] T03 — Fix the two existing consumers

- Depends on: T02. Files: `scripts/acquisition_ledger.py`, `scripts/reference_coverage.py`.
- Do: make `build()` promote readings only for the explicit inspected-access allowlist with a nonempty locator, preserving a prior legitimate day-1 assessment if a later access fails. Make `novelty_axes()` iterate the four canonical axes for every source and conservatively handle access, locator and state as specified. Keep the small allowlist local to each consumer; no new module, dependency or CLI. Preserve the native-response audit, denominator rules and deterministic ordering.
- Done when: focused regressions pass. Record the planned temporary staleness of derived JSON until T12; do not claim a green full suite, weaken existing reproduction tests or repeatedly regenerate intermediate research outputs.

### [x] T04 — Resolve the three follow-up identities

- Depends on: T01. Files: execution `sources.json`.
- Do: verify S1/S2 metadata by DOI and resolve S3 through the bounded Crossref lookup and publisher confirmation. Preserve request parameters, returned identifiers, dates and why the selected record matches. Acquire accessible primary text via the frozen routes, retaining raw/extracted bytes and hashes.
- Done when: each identity is confirmed or explicitly ambiguous/unavailable. Publication years and source versions are observed; missing metadata does not get invented. No novelty assessment is made from a title or abstract.

### [x] T05 — Assess UAVConfigFuzzer first

- Depends on: T03, T04. Files: `docs/day3-reading-records.json` (S1), execution `sources.json`.
- Do: inspect the threat model, configuration-generation method, tested autopilots, fault stimuli and evaluation sections actually available. Record all four axis judgments, especially whether configuration fuzzing establishes equivalent recovery intention across configurations.
- Done when: each judgment has a rationale and exact locator, or is unresolved with access details; the record agrees with the retained text and manifest. Stop after a source/section checkpoint if interrupted.

### [x] T06 — Assess ADGFuzz

- Depends on: T05. Files: reading records (S2), execution `sources.json`.
- Do: inspect available method, inputs/policies and evaluation sections; distinguish generated tests, trace observations and calibrated recovery coverage. Apply all four axes without changing their definitions after seeing results.
- Done when: S2 meets the same evidence contract, including unresolved axes where warranted.

### [x] T07 — Assess PGPatch

- Depends on: T06. Files: reading records (S3), execution `sources.json`.
- Do: inspect the verified work's specification/patching method and evaluation; distinguish patching a policy from composing configured recovery behavior. Keep the verified year and DOI, not the inherited “2026” label.
- Done when: S3 meets the same evidence contract; ambiguity or inaccessible text leaves the relevant reading unresolved rather than substituting a similarly named paper.

### [x] T08 — Pin and inspect U3's artifact tree

- Depends on: T01. Files: execution `sources.json`; U3 in reading records.
- Do: inspect `https://github.com/purseclab/PGFuzz` at a recorded full commit SHA in the local source cache. List the tree, then open README/setup instructions and locate actual policy, parameter/configuration, fault-input, oracle/logging and autopilot integration files. Record exact paths and per-file hashes as opened; do not invent paths from the paper.
- Done when: a pinned file inventory or a precise access failure exists. No install, container launch, executable from the repo, or claim of runtime compatibility is required.

### [x] T09 — Record U3 findings and a reuse decision

- Depends on: T08. Files: U3 reading record; execution `README.md`.
- Do: trace the relevant static call/configuration path across the inspected files. Resolve all four axes as far as those files permit, leaving unavailable or untraced behavior unresolved. Recommend reuse of specific policies/interfaces/oracles, adaptation, or no suitable component, with pinned file evidence and untested compatibility clearly stated. Relate this to the already reviewed U5/U6 tooling options without implementing a launcher.
- Done when: each judgment and reuse recommendation is source-linked; absence in inspected files is not absence in the whole repository or a verified execution result.

### [x] T10 — Reconcile the existing U1–U12 axis findings

- Depends on: T05–T07, T09. Files: reading records; execution `sources.json` and `README.md`.
- Do: review every existing record against the clarified axes in source-sized checkpoints. Start with U6/U9's `coverage: none` versus affirmative states, then U1/U2/U4's distance/oracle distinctions, U7's liveness placement and U11's heartbeat-only finding. Re-open primary locators for every changed assessment. Add missing axes explicitly, preserving unrelated earlier findings and acquisition dates; record each reinspection date and old → new judgment with reason.
- Done when: prose, axis states and access scope agree for each record. Unavailable supporting text leaves the disputed judgment unresolved. No global keyword remapping or semantic conclusion drawn merely from a passing checker.

### [x] T11 — Screen the complete retained metadata intake

- Depends on: T10. Files: new execution `candidate-screening.csv`; reading records only for newly identified unresolved C entries.
- Do: screen the 317 raw hits in ascending index, in resumable batches of 25 or fewer. Use the frozen relevance rules and only the retained metadata for this pass. Map exact identities to inspected U/S sources, document exclusions/duplicates, and expose relevant unread or ambiguous candidates as specified above. Do not expand to new searches or silently start a new full-text campaign.
- Done when: every retained row is accounted for exactly once, input indices/IDs agree with the hashed export, and all relevant unread work is visible in the reading records and closeout blockers. Screening metadata is not full-text review.

### [x] T12 — Regenerate and reconcile derived evidence

- Depends on: T03, T10, T11. Files: both existing generated JSON outputs; `docs/reference-coverage-2026-09-12.md`.
- Do: run `python scripts/acquisition_ledger.py` and `python scripts/reference_coverage.py`; never hand-edit their JSON. Run both `--check` modes. Reconcile the document's currently asserted coverage figures and axis table against the new JSON, including the existing stale 2/6 historical-credit and `supported_bounded` statements. Clearly mark superseded passages and add a dated current-result subsection instead of leaving competing “current” tables.
- Done when: subsequent regeneration leaves both artifacts byte-identical; all 402 historical rows and 90 provenance gaps remain, canonical export stays `day4_public`, known-reference coverage remains 3/6, rejected historical credit stays 0/6, and the frozen register/raw-export hashes remain unchanged. New readings affect assessments, not discovery recall. The current prose/table agrees with the JSON.

### [x] T13 — Write the URC-01 decision against its real acceptance criteria

- Depends on: T12. Files: `docs/prior-art.md`; execution `README.md`.
- Do: add dated provenance-linked executed database and patent-domain web search strings; relevance inclusion/exclusion and access limitations; a comparator table with identity/version, pinned configurations, equivalent-intent rule, loss stimulus, reconnection, coverage endpoint, available code and exact source locators. Cover all U/S sources and summarize/link unresolved C entries. Distinguish partial ingredient overlap from evidence addressing the precise remaining combination.
- Done when: every clause of URC-01's done-when has an evidence link or is explicitly unmet. Record the evidence conclusion and independent gate status using the frozen rule. An unread threatening competitor, missing required search or unsupported conclusion keeps URC-01 open; do not amend its acceptance text to declare success. Specify the next bounded work, not an automatic downstream start.

### [x] T14 — Make the review packet navigable

- Depends on: T13. Files: `docs/SPRINT_TASKS.csv`, `docs/SPRINT_PROGRESS.md`, `docs/REVIEW_READY.md`, `docs/START_HERE.md`, `README.md`, execution `README.md`/`sources.json`.
- Do: add one `URC-R03` Agent row depending on URC-R02 for this packet, with actual acceptance/evidence and a separate URC-01 state in its explanation. Add one dated progress and review entry. In the README/start guide, add only a short current-review pointer and correct any present-tense statement directly superseded by this work; keep dated historical evidence accessible. Finish the command/exit, source-hash, decision-change and unresolved-work records.
- Done when: a cold reader reaches the current result and can distinguish completed review operations, unread sources, unresolved URC-01 conditions and owner-only tasks. No old report is silently rewritten as if today's review happened earlier.

### [x] T15 — Exercise integrity controls and the full gate

- Depends on: T14. Files: existing two test modules; execution `README.md`.
- Do: add a compact acceptance check in `tests/test_reference_coverage.py` for unique IDs, mandatory U1–U12/S1–S3 presence, exactly four valid axis states per record, all-unresolved states for unread access, and the complete candidate-screening index/ID accounting with valid reading links and reasons. Use the evidence directory fixed at T00. Preserve the existing native-response tamper test. In a disposable copy remove S1 while leaving generated JSON intact: both `--check` commands must exit nonzero. Then regenerate in that copy: the required-ID check must still fail, proving that regenerated omissions cannot look complete. Restore a pristine copy for each control.
- Done when: intended failures are recorded separately from real gate failures, restored inputs pass, deterministic regeneration holds, and all commands below exit zero in the implementation checkout. Verify the full manifest hashes against locally retained snapshots and the reading-record prefixes; CI can check metadata relationships, not access private cached copies. Software checks establish consistency, not correct paper interpretation or novelty; manually compare each changed finding with its retained locator and record this as executor self-review.

### [x] T16 — Publish the implementation handoff

- Depends on: T15. Files: plan checkboxes and implementation PR description.
- Do: commit the bounded implementation and push one PR to main. Link the merged replacement-plan commit, actual implementation commits, execution evidence, critical findings, URC-01 status and remaining work. Check hosted CI for the final pushed head; update the task delivery record without embedding a commit's own hash inside itself.
- Done when: the implementation PR is reviewable with green checks on its actual head and no unsupported completed-gate language. Opening a PR is not a merge; follow the user's active merge instruction, and never merge a failing head or start downstream work just because CI passed.

## Gate commands

Use Python 3.11 with `jsonschema==4.26.0` from `requirements.txt`; on this machine the reviewed environment is `/Users/redhose/ENTER/bin/python`. Record the executable actually used. These are existing repository commands; no new lint/typecheck/build framework is required.

```sh
python -m unittest discover -s tests -q
python scripts/check_repo_contract.py
python scripts/acquisition_ledger.py --check
python scripts/reference_coverage.py --check
python evidence/task-2026-09-09/rerun_search.py --audit evidence/task-2026-09-11-public/database-export.json
python tools/check_presentation.py . "UAV Failsafe Composition" uav-failsafe-composition
python tools/test_presentation.py
git diff --check
```

Historical-export rejection is an expected control, not a reason to change the raw data. The candidate evaluator under `evidence/sprint-2026-09-05/` binds a historical candidate and is excluded from the current gate; make no claim that it passes. If main has an unrelated failure, record the exact baseline and report verification incomplete instead of silently expanding this plan or weakening a check.

## Requirement traceability and acceptance

| Requirement | Tasks |
| --- | --- |
| Procedure precedes new judgments; input identities and dates remain auditable | T00–T01, T04, T08 |
| Named follow-ups and U3 reviewed with truthful access and a reuse decision | T04–T09 |
| Unread/missing-axis evidence cannot masquerade as a supported gap | T02–T03, T10, T15 |
| Retained intake has no silent exclusions; reference denominator stays fixed | T01, T11–T12, T15 |
| Existing prose/axis contradictions are resolved from sources | T10, T12–T14 |
| Actual database/patent-search history and conditional URC-01 outcome | T13–T14 |
| Deterministic artifacts, useful negative controls, complete local/hosted checks | T12, T15–T16 |

**Packet acceptance:** all planned operations have an observed outcome, required sources and intake rows are accounted for, derived evidence is reproducible, the current narrative agrees with the inspected evidence, and verification is reported accurately. Missing accessible work is unfinished, not an access blocker. Unavailable text and newly identified relevant unread sources stay named and unresolved. Packet completion never implies URC-01 completion.

**URC-01 acceptance:** its actual research criteria and relevant dependencies are satisfied and the evidence supports an allowed conclusion; otherwise record partial/blocked with exact remaining work. No automatic promotion of URC-S08, URC-02 or any experiment follows this plan.

## Out of scope

- URC-S08 resource/configuration/advisor choices; configured-vehicle matrix, simulator installation, harness, traces, hardware and measurements.
- New broad searches, new native-export query legs, a native patent-search campaign, purchases, outreach or legal clearance.
- Re-pinning historical `candidate.json`, changing raw exports or the day-1 reference set, new parsers/frameworks, or a repository-wide cleanup.
- Closing PR #6, rewriting old repository names throughout historical docs, or merging PR #12 alongside this replacement. Publishing the requested plan/implementation PRs is distinct from publishing a scientific novelty claim.

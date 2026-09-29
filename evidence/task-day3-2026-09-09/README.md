# URC-D03 — bounded preparation evidence

Date: 2026-09-09. Base (both reviewed PR layers merged): `39578d6ef1ee765bcd53c7b2f0ba940b3f0d367f`.
Branch: `task/day-three-20260909`. Scope: Converge source provenance and narrow the research question.

## Delivered change

Six new ledger tests preserve both acquisition routes, unknown historical query mappings, zero-result versus positive query support, unscreened status despite raw flags, all raw rows and deterministic regeneration. 21 tests and repository contract pass. All 402 raw rows retained; 90 provenance holes remain. This is not full novelty closeout.

See [plan](https://github.com/500ft/uav-failsafe-composition/blob/4ff22d19295cda3757afeb162496b9c3a1ad82e9/docs/DAY3_PLAN.md) and [primary deliverable](../../docs/day3-source-review.md). Status is maintained only in [SPRINT_TASKS.csv](../../docs/SPRINT_TASKS.csv); original research/CAD gates remain unchanged. Delivery is a new PR, not an automatic merge or scientific release.

## Verification and reproducibility

Tool `wall_time_seconds` fields describe individual output/poll waits, not total command runtime; use the test runner's printed duration where available. All new/modified Markdown local links and the 13-column task ledger were checked successfully before commit. No separate independent reviewer participated in this task.

[checks.json](checks.json) records commands, observed exit statuses and selected outputs. Baseline source identity, command and outputs are in [baseline.json](baseline.json). Local Python is 3.11.8; CAD tests use the registered isolated Python 3.11.16/CadQuery toolchain. On another machine use the repository's existing workflow/dependency setup, not this machine's absolute interpreter path. The local pytest readline stub is recorded explicitly.

The listed relevant local checks completed. The P-V publication-mode exit 2, where present, is the expected blocked state, not a test failure.

No separate type/lint task was added: existing configured compile/tests and source-specific checks were used. Tests use synthetic developer cases; they are not independent human review, experimental results, adoption or held-out research evaluation. Source checks distinguish read sections from whole-paper review. Initial missing-module test failures for new tooling reflect tests written before implementation, not a defect in the old product. Prior scientific artifacts were not regenerated as new evidence.

## Remaining project work

URC-01/D02 provenance and exact-gap closeout stay unresolved unless their full acceptance evidence exists.

The only research findings here come from identified external sources; no downloaded third-party full text or sensitive raw data is committed. AI review and declared metadata do not substitute for authorship, permission, calibrated measurement or independent assessment.

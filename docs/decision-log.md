# Decision Log

## 2026-10-06: adopt the control-prototype deployment investigation

The owner authorized implementation of the reviewed v2 software pivot and
repository reconciliation. The adopted question is: which defects remain after
a costed back-to-back comparison at numerical, stateful and integration
boundaries, and which additional checks reduce them? Generation method and
verification method remain separate factors. Reset and timing behavior belong
in B2B whenever its boundary includes their state and histories.

The successor starts in local sibling staging named `control-code-verification`.
Its public repository name is pending in the external `owner-replies.md`; no
public successor has been created. This repository retains its failsafe results.
Study A is paused pending an explicit release or closure choice. The owner has
not declared Study A complete, authorized a release, or supplied physical
readiness, funding or purchase decisions. The second reviewer remains pending.

This direction supersedes the active status of the earlier switch questions
U1–U3 and the fleet-envelope questions. Those questions are closed as
superseded, without answers or mission-requirement claims. The similarly named
protocol property IDs and the D7 evidence gate retain their original meaning.
The [history index](../history/README.md) preserves the prior work and its
unmet gates. The [roadmap](../ROADMAP.md) records the current owner step.

Source: the owner task issued on 2026-10-06, implementing
`REPO_PLANS_20261006_v2.md` §5.1 with the corrections in `REVIEW.md` and
`RESEARCH_OBJECTIONS_AUDIT_20261006.md` (external handoff files). PR #50
remains the source of the latest datalink qualification and documentation
corrections. This change depends on that PR and does not replace it.

## 2026-09-03 — Use the configured vehicle as the experimental identity

**Decision:** analyze autopilot + firmware + airframe + complete parameters rather than “PX4 versus ArduPilot.”

**Reason:** both platforms expose configurable failsafe actions and delays. A brand comparison would confound software, tuning, airframe, and intention.

## 2026-09-03 — Narrow the candidate contribution

**Decision:** focus on empirical post-authority-loss recovery contracts.

**Rejected framing:** generic capability-aware fleet safety, health contracts, or recovery reservations.

**Reason:** those ingredients have close prior art. The more defensible question concerns native mode transitions and recovery trajectories after companion authority disappears.

## 2026-09-03 — Start with a conformance benchmark

**Decision:** run a matched SITL pilot before building a fleet allocator.

**Reason:** if individualized native behaviors do not materially change the recovery envelope, fleet optimization would add complexity without evidence of value.

## 2026-09-03 — Keep physical flight contingent

**Decision:** physical testing is a later, facility-approved gate.

**Reason:** the present repository contains no flight evidence, approved test plan, or demonstrated operating envelope.

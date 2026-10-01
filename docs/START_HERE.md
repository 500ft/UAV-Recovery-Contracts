# Start here — UAV Failsafe Composition

[Project overview](../README.md) · [Run the checks](../README.md#quick-start) ·
[Roadmap](../ROADMAP.md) · [Review index](REVIEW_READY.md)

## In one minute

When a drone loses its command link or companion computer, the autopilot's own
failsafe logic takes over. What it does depends on the firmware, airframe,
parameters and the exact failure, so the unit of study here is a pinned PX4
build with a complete parameter set.

The project has a Python model of PX4's failsafe logic, written from the
source. It agrees with PX4's compiled `Failsafe` class on 11 of 11 input
sequences. The simulator harness now reproduces PX4's failsafes (Hold, then
RTL after a datalink loss) after a parameter-encoding bug in the harness was
fixed. The next step is Study A: every required single-event simulator cell compared
with the model, judged by a coverage gate. Everything so far is simulation.

## Reading paths

| If you have | Read |
| --- | --- |
| Five minutes | The [README](../README.md), then the [roadmap](../ROADMAP.md) |
| Half an hour | The [Study A protocol](specs/formal-composition/study-a-protocol.md) and its [decisions](specs/formal-composition/decisions-2026-09-19.md), then the [differential record](../evidence/task-differential-2026-09-29/README.md) |
| A review to do | The [review index](REVIEW_READY.md) |
| A question about a number | The [traceability index](traceability.md) and the [number-provenance audit](number-provenance-audit-2026-09-25.md) |
| A question about novelty | The [source review](day3-source-review.md), then [prior art](prior-art.md). The novelty question is still partly open: 17 intake records are unread |

## How the question narrowed

The project started as a fleet question: can each vehicle's own recovery
behaviour be reserved in less airspace than one worst-case envelope? The
[source review](day3-source-review.md) found existing work on trajectory
profiling, shared simulator integrations and reconnection handling, which
narrowed the question. The 2026-09-24 critique then dropped the second
autopilot (ArduPilot), because PX4's own behaviour wasn't explained yet.

What remains is Study A, then a benchmark release. The envelope and fleet
questions, with their original decision rules, are kept in
[Experiment 01](experiment-01-authority-loss.md) and the
[research plan](research-plan.md) as later work.

![Original decision diagram: configured authority loss to measured recovery and a held-out gate, keeping a global envelope when individual envelopes don't justify expansion](../assets/recovery-contracts-overview.svg)

*The original decision diagram for the envelope study, kept because it shows
the alternative outcomes. It is not a result.*

## Where things live

- [Roadmap](../ROADMAP.md): finish line and remaining steps.
- [Long-term backlog](TASKS.md): later tasks, including hardware work.
- [Decision log](decision-log.md): directions that were dropped, and why.
- [Claim ledger](claim-ledger.md): each claim and its evidence.
- [CONTRIBUTING.md](../CONTRIBUTING.md): evidence language, sources and the
  public-disclosure boundary.
- The September 11 [acquisition correction](ACQUISITION_CORRECTION_2026-09-11.md)
  explains which early deliverables were preparation rather than finished work.

Any flight test would need a site risk assessment and facility approval first.
Passing CI does not authorise a flight.

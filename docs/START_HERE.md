# Start here — UAV Failsafe Composition

[Project overview](../README.md) · [Run the checks](../README.md#quick-start) ·
[Roadmap](../ROADMAP.md) · [Review index](REVIEW_READY.md)

## In one minute

When a drone loses its command link or companion computer, the autopilot's own
failsafe logic takes over. What it does depends on the firmware, airframe,
parameters and the exact failure, so the unit of study here is a pinned PX4
build with a complete parameter set.

The Python model agrees with the compiled PX4 failsafe class on the
[fresh reserved corpus](../evidence/task-domain-2026-10-03/results.json), within
its [declared input and state domain](../evidence/task-domain-2026-10-03/README.md#domain-recorded-before-execution).
The repaired integer transport restores Hold then RTL in the
[datalink SITL case](../evidence/task-runtime-2026-09-29/README.md). The
[fresh matched builds](../evidence/task-observation-qualification-2026-10-04/README.md)
recover the instrumented datalink path; the earlier tracking failure's cause
remains unknown and injection timing remains open above.

The [public-log inspection](../evidence/task-public-flight-2026-10-04/README.md)
reconstructs a sampled geofence event. It admits no replay or native comparison:
firmware, input-history and domain exclusions remain. This is distinct from
component agreement, integrated SITL qualification and vehicle-level validation.
No physical validation or Study A confirmation has run.

The [owner direction](decision-log.md#2026-10-06-adopt-the-control-prototype-deployment-investigation)
pauses Study A and adopts a separate software deployment investigation.
The [roadmap](../ROADMAP.md) records the release/closure and successor-name
choices still needed. Source cross-checks by an AI agent do not constitute
independent human review.

## Reading paths

| If you have | Read |
| --- | --- |
| Five minutes | The [README](../README.md), then the [roadmap](../ROADMAP.md) |
| Half an hour | The [Study A protocol](specs/formal-composition/study-a-protocol.md) and its [decisions](specs/formal-composition/decisions-2026-09-19.md), then the [declared-domain result](../evidence/task-domain-2026-10-03/README.md) and [runtime qualification](../evidence/task-observation-qualification-2026-10-04/README.md) |
| A review to do | The result packets above, then the historical [review index](REVIEW_READY.md) |
| A question about a number | The [traceability index](traceability.md) and the [number-provenance audit](number-provenance-audit-2026-09-25.md) |
| A question about novelty | The [source review](day3-source-review.md), then [prior art](prior-art.md). The novelty question is still partly open: 17 intake records are unread |

## How the question narrowed

The project started as a fleet question: can each vehicle's own recovery
behaviour be reserved in less airspace than one worst-case envelope? The
[source review](day3-source-review.md) found existing work on trajectory
profiling, shared simulator integrations and reconnection handling, which
narrowed the question. The 2026-09-24 critique then dropped the second
autopilot (ArduPilot), because PX4's own behaviour wasn't explained yet.

Study A and the earlier envelope questions are preserved in the
[history index](../history/README.md). Obsolete diagrams and alternate plans
have been deleted from the working tree; the history index links their
immutable versions.

## Where things live

- [Roadmap](../ROADMAP.md): finish line and remaining steps.
- [History index](../history/README.md): retired proposals and retained evidence.
- [Decision log](decision-log.md): directions that were dropped, and why.
- [Claim ledger](claim-ledger.md): each claim and its evidence.
- [CONTRIBUTING.md](../CONTRIBUTING.md): evidence language, sources and the
  public-disclosure boundary.
- The September 11 [acquisition correction](ACQUISITION_CORRECTION_2026-09-11.md)
  explains which early deliverables were preparation rather than finished work.

Any flight test would need a site risk assessment and facility approval first.
Passing CI does not authorise a flight.

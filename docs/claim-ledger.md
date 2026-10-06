# Claim Ledger

The ledger controls what the repository may say as evidence changes.

| Claim | Current evidence | Language permitted now | Evidence needed to strengthen it |
| --- | --- | --- | --- |
| Failsafe behavior is configuration-dependent | Official platform documentation | “PX4 and ArduPilot expose configurable failsafe behavior.” | None for the documentation claim |
| Uncoordinated recovery can create fleet conflicts | Official incident investigation and contingency literature | “Fleet-level composition is operationally motivated.” | None for motivation; local risk still requires testing |
| The exact proposed gap is globally novel | Bounded prior-art review, URC-01 gate *partial* (2026-09-15): prior art found on the reconnection and liveness axes as documentation; equivalent intent and coverage unsettled with 17 unread intake rows; [targeted formal-composition contrasts](prior-art.md#current-px4-comparison) added, without a novelty verdict | “Candidate contribution” or “working gap” | Reading of the unread rows; native patent search; dissertation and standards searches |
| The Python model agrees with the native failsafe class | [Reserved-corpus results](../evidence/task-domain-2026-10-03/results.json), with development failures and repairs retained | “Exact agreement on the executed reserved corpus within the [declared domain](../evidence/task-domain-2026-10-03/README.md#domain-recorded-before-execution)” | Separately qualified inputs and fresh verification before extending the domain; no universal equivalence claim |
| The integrated datalink response is observable in SIH SITL | [Transport repair](../evidence/task-runtime-2026-09-29/README.md) and [fresh-build qualification](../evidence/task-observation-qualification-2026-10-04/results.json) | “Hold then RTL in the exercised development case; instrumented datalink stages recovered” | Remaining mechanism inputs and a frozen discrete model comparison; timing stays non-gating under §7b |
| An extracted PX4 model reproduces all required Study A cells | Confirmation has not run; [prerequisites](../evidence/task-observation-qualification-2026-10-04/prerequisite-inspection.json) remain | “Study A paused; confirmation incomplete” | All applicable D25 cells frozen before execution and valid, observable, classified under [D7 and §7b](specs/formal-composition/study-a-protocol.md#7b-amendment-2026-09-30--success-criterion-after-the-decision-sign-off); unresolved discrepancies block their subdomains |
| A public event can be reconstructed and replayed | [Sampled reconstruction and replay exclusions](../evidence/task-public-flight-2026-10-04/results.json) | “Sampled geofence timeline reconstructed; no admitted replay or native comparison” | Version-compatible source, parameter completeness and consumed-input history; independent human reconstruction check pending |
| Native agreement establishes mission safety or physical reserve | No such validation | Prohibited from these results; logged SOC is an estimate | Explicit mission requirements and separately observed outcomes; maneuver reserve needs its own calibration |
| Equivalent intentions produce different native traces | None | “Hypothesis” | Pinned SITL, HITL, and preferably physical traces |
| Configuration-specific tubes retain coverage | None | “Planned evaluation” | Held-out coverage with uncertainty |
| Individual tubes reserve less volume | None | “Proposed comparison” | Paired held-out comparison at matched coverage |
| Fleet evacuation improves safety-efficiency | None | “Proposed fleet experiment” | Held-out fleet encounters and physical validation |
| The system is safe | None | Prohibited | Defined operational envelope, safety argument, and appropriate validation |

The [owner direction](decision-log.md#2026-10-06-adopt-the-control-prototype-deployment-investigation)
supersedes the earlier active switch and fleet questions. The table preserves
prior-study claims; Study A is paused and remains incomplete. The separate
successor's numerical evidence stays in local staging until its name is authorized.

## Evidence-state vocabulary

- **Literature:** supported by a cited source, not reproduced here.
- **Planned:** specified but not run.
- **Simulation:** generated in a software environment with pinned provenance.
- **Public-log reconstruction:** observations extracted from third-party logs, with
  firmware, missing inputs and sampling limits stated. This label does not imply
  admitted replay, native comparison or independently verified physical outcomes.
- **HITL:** generated using flight-controller hardware in a controlled rig.
- **Measured:** produced by a physical experiment under a documented protocol.

A stronger label never replaces the need to state its scope and conditions.

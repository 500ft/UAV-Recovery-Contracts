# Public-flight feasibility

Three downloaded logs yielded one sampled geofence timeline and no admitted
model replay. In that event, the recorded Hold-to-RTL commit interval was
about 5.005 seconds. [results.json](results.json) holds the observations,
parameter values, firmware identities, hashes, sample gaps and exclusions.
This is executed development work.

## Selection and provenance

[selection.json](selection.json) was recorded before the metadata search.
The official browse interface was queried for the existing firmware pin and
event terms. Its returned-row counts are in the results; these are query rows,
not an independent-flight denominator. Keyword searches were also inspected
despite available generic pin matches. The three download choices were then
recorded in the local source manifest before any ULog was parsed. There was no
held-out evaluation or acceptance threshold.

| Candidate | Observed outcome | Replay disposition |
|---|---|---|
| A, pin search | Firmware matches the current pin; hardware reports PX4_SITL. No failsafe flag topic or observed failsafe | Excluded as a public-flight event. Default-profile membership does not prove that a topic was captured |
| B, datalink search | RC loss precedes and overlaps datalink loss on a different revision | RC is outside the admitted domain; cannot attribute the resulting mode sequence to datalink alone |
| C, geofence search | Geofence flag rises in Altitude mode, followed by Hold and RTL; it clears before a later Position-mode takeover | Sampled event reconstructed at its own revision. Missing update history prevents the required replay |

[sources.json](sources.json) pins the retrieval implementation and matching
firmware source files. Each ULog contains a full git revision and release,
hardware-family and toolchain metadata. The executing firmware binary was not
provided, so its hash and any unrecorded local build changes remain unknown.
The full typed initial parameter records and all recorded changes were exported
beside each raw log. Only an allowlist is published. PX4's
[parameter writer](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/logger/logger.cpp#L2228)
records used parameters; this is not proof of a complete binary parameter
inventory. Candidate C has no recorded parameter changes.

## The geofence event

The relative timeline is in `geofence_observation` and candidate C's topic
transitions in the results. All times share that vehicle's boot clock and use
the ULog header start as zero. Cached samples and a prior mode commit can
precede zero. No absolute flight time is exported.

The last sampled false and first sampled true `geofence_breached` values
bracket the observed flag change. The following `vehicle_status` records
contain a Hold commit and then an RTL commit in `nav_state_timestamp`.
`navigator_status` subsequently reports RTL. After the sampled flag clears,
RTL persists until the recorded mode intention changes and takeover is
reported. That persistence is consistent with the revision's geofence action
remaining active until mode change or disarm.

The matching source gives this path:

| Stage | Source and observation limit |
|---|---|
| Geometry to detector result | [Navigator](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/navigator/navigator_main.cpp#L913) evaluates the fence on its scheduled loop, subject to the [check interval](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/navigator/GeofenceBreachAvoidance/geofence_breach_avoidance.h#L42). `geofence_result` is absent. No geometric crossing or detector-publication time is reconstructed |
| Detector result to failsafe input | [GeofenceChecks](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/commander/HealthAndArmingChecks/checks/geofenceCheck.cpp#L38) combines the detector's breach bits. [Health checks](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/commander/HealthAndArmingChecks/HealthAndArmingChecks.cpp#L102) publish flags on changed results or after their periodic interval, rather than on every selector update |
| Input to selected action | [Failsafe](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/commander/failsafe/failsafe.cpp#L86) maps the configured geofence action to RTL and mode-change/disarm clearing. The [framework](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/commander/failsafe/framework.cpp#L53) also uses update history, delay state and takeover requests. No per-update selected-action trace was recovered; the mode output was not substituted for this input history |
| Selected action to committed mode | [Commander](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/commander/Commander.cpp#L2309) maps action and intended mode, and stamps changed nav state. That recorded commit stamp is distinct from the later status publication timestamp |
| Committed mode to navigator report | [Navigator status](https://github.com/PX4/PX4-Autopilot/blob/94cb2012792b2ae89f0b147cfee53ee31ae550be/src/modules/navigator/navigator_main.cpp#L1370) reports its mode. It does not measure actuator response or physical recovery |

The logged flag-to-RTL interval and the wider adjacent-sample bracket are both
reported. Neither is a geometric-breach-to-response latency. Unlogged toggles
and scheduler delays remain possible. Logger dropout records are absent, but
that does not establish lossless observation of every publication.

## Logger and replay limits

All inspected revisions include `failsafe_flags`, `vehicle_status` and
`navigator_status` in their default profile without added topic throttling;
telemetry has a separate configured interval. See the pinned logger files in
the source manifest and candidate-specific measured gaps in the results.
Candidate A nevertheless omits those flags. A custom
[`logger_topics.txt`](https://github.com/PX4/PX4-Autopilot/blob/d6f12ad1c4f70ad3230afd7d86e971421e02fef4/src/modules/logger/logged_topics.cpp#L532)
can replace profile selection. Its actual file and logger command line are
unavailable, so the cause of that omission is unknown.

Candidate C starts with the vehicle already armed. The log provides sampled
flags, mode intention and committed mode, but not the pre-arm selector state,
every consumed flag update, or every same-mode request and stick-takeover
consumption. Event notifications are present; they do not expose each selector
invocation. Missing `geofence_result` separately blocks detector timing.
Its older firmware and mode-changing history also fall outside the
[existing adapter domain](../task-domain-2026-10-03/README.md#domain-recorded-before-execution).
The older `local_position_accuracy_low` field was retained under its actual
name. No adapter was extended and no native class was built for these logs.
These are observability and domain exclusions, with no model-mismatch verdict.

The next acquisition needs a permitted event log on the existing pin with
pre-arm history and the admitted mechanism, plus its logger configuration and
the consumed inputs needed for replay. Otherwise a separately authorized
version-specific adapter and an explicit treatment of unobserved updates are
needed before comparison. This result leaves the Study A coverage gate,
confirmation seeds and separate instrumented-runtime fault unchanged.

## Reproduce and attribution

Set `UAV_PUBLIC_LOG_CACHE` to the retained external directory containing
`candidate-a.ulg`, `candidate-b.ulg`, `candidate-c.ulg`, the source manifests
and the selection registration. With the extraction environment recorded in
the results:

```sh
python evidence/task-public-flight-2026-10-04/analyze.py "$UAV_PUBLIC_LOG_CACHE" > /tmp/uav-public-results.json
cmp /tmp/uav-public-results.json evidence/task-public-flight-2026-10-04/results.json
python -m unittest discover -s tests -p test_public_flight_observation.py
```

The owner's reproduction exercise is to explain the sampled geofence flag,
Hold commit, RTL commit and navigator report from candidate C, including why
the flag bracket cannot locate the geometric crossing. Public summaries alone
cannot recreate missing causal inputs.

[checks.json](checks.json) retains validation, including the initial failures.
The old repository check required a statement that no flight data existed.
Its wording was corrected after these public logs were inspected; the Study A
notice remains enforced. A raw-log re-extraction reproduced the results, and
the new fields and files were audited for location and identifier leakage.

Derived observations credit **PX4**, from [Flight Review](https://review.px4.io/),
under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/), as specified by
the [official data documentation](https://docs.px4.io/main/en/dev_log/flight_log_analysis_statistical)
and public-upload terms. Changes: fields selected, locations and identifiers
omitted, time origin shifted, transitions and gaps summarized. The local
source manifest retains the individual source URLs, retrieval dates and
hashes. Raw logs, full parameter records and downloaded pages stay outside
git. Flight Review's software license is separate from this data license.

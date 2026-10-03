# Prospective runtime diagnostic

Recorded before building or executing the development runs. This is FINAL_PLAN
4.1 task 3, following the signed Study A protocol section 7b and decisions
D16, D23, D24 and D30. No confirmation data or frozen seeds are used.

Run three independent local SIH processes in Auto Loiter with the existing RTL
configuration and datalink-loss stimulus. Development labels 101, 102 and 103
use explicit offsets 0.0, 0.4 and 0.8 seconds from the runner's nominal schedule.
No random generator is involved. Retain every attempted run. A setup/build
failure stops execution for diagnosis; do not substitute a successful run.

## Snapshot criterion (NP-4)

Before arming, read every name in this build's generated parameter registry,
including unused parameters, using PARAM_REQUEST_READ by name. The generated
parameters.xml name/type set must equal the compiled px4_parameters.hpp enum.
A complete snapshot contains exactly that set, one decoded INT32 or REAL32 value
per name with the matching returned type, and the transported float bytes in
hexadecimal. No inferred default fills a missing reply. Preserve partial output
on failure and fail setup before arming. Existing override readback and bytewise
integer transport remain in use. Record the registry hashes and the snapshot
hash with each execution. This is a sequential pre-arm read, not an atomic
snapshot or a guarantee that parameters never change in flight. Record its
host interval; cached telemetry stamps do not bound its vehicle interval above.

## Measurement and conditional calibration (NP-3, NP-6)

Trace the pinned receive, heartbeat-aging, telemetry-publication, commander,
failsafe and navigator paths before execution. Instrument only observations:
last qualifying GCS receive; heartbeat-age check; telemetry publication;
commander timeout evaluation; consumed flag; selected action; committed mode;
and navigator mode execution/setpoint publication. Use PX4 hrt_absolute_time
microseconds throughout. Record entry/exit brackets where distinct calls can
share a simulated timestamp. Report observed adjacent gaps, not nominal-rate
upper bounds. A missing log is unknown. Navigation response means executing
the selected navigator mode and publishing its setpoint, not motion or landing.

Decompose last receive to final qualifying telemetry anchor, anchor to detector,
detector to consumed flag, flag to Hold/RTL selection, selection to committed
nav_state, and commitment to navigator response. Compare source timer semantics
with these intervals, retaining late updates and incomplete observations.
The pre-existing flag-to-selection segment alone cannot explain total latency.

Calibration may describe repeatability of directly observed native segments.
It cannot calibrate host cut-to-response accuracy: the cached host-trigger stamp
has no defensible upper bound, and a subsequent telemetry packet is not an
acknowledgment of the cut. If this remains true, report segment measurements and
leave timing outside pass/fail, with no replacement tolerance. Do not infer a
population quantile from these diagnostic repeats. Preserve historical 1.5 s
re-analysis tolerance and the signed protocol's historical timing thresholds.

Stop after these development runs and relevant checks. Do not expand to other
hazards, timing experiments, Study A confirmation, or upstream defect claims.

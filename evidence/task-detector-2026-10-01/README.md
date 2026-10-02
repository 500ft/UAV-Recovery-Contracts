# Datalink detector timing

Three retained development runs put RTL 5.016 s after Commander reports GCS
loss. The instrumented run records 5.004 s from consumption of the loss flag
to selection of RTL. The extra interval before detection comes from a timer
origin omitted by the earlier prediction: Commander refreshes its timer from
telemetry-status publications while the receiver still considers a heartbeat
present.

[results.json](results.json) holds the measured timestamps and intervals.
This analysis reuses the corrected instrumented run, its uninstrumented
counterpart and the full-parameter capture. No experiment was repeated.

## Source and observations

[source.json](source.json) retains excerpts, line numbers and full-file hashes
from the pinned PX4 commit. The path is:

1. `MavlinkReceiver::handle_message_heartbeat` saves the reception time.
2. `CheckHeartbeats` keeps `heartbeat_type_gcs` true through
   `HEARTBEAT_TIMEOUT_US`. Periodic checks can further delay clearing it.
3. `Mavlink::publish_telemetry_status` stamps each publication with the current
   vehicle time. It can publish again while that flag remains true.
4. `Commander::dataLinkCheck` copies each positive publication timestamp into
   `_datalink_last_heartbeat_gcs`. Loss requires strictly more than
   `COM_DL_LOSS_T` since that refresh.
5. The health check copies the status into `failsafe_flags`. In the Commander
   loop, action selection precedes that health update, so consumption can occur
   on a later iteration. The instrumented run records this distinction.

In each capture, the observed loss lies between the last logged positive and
first logged negative telemetry-status timestamps, each shifted by the
configured timeout. That is consistent with the source path. The previous
prediction started the timeout directly at the last received heartbeat and
left out the qualification and publication stages. This is a guard-input
timing assumption in the experiment, separate from the tested selector logic.

## Reproduce

The default report uses Python's standard library:

```sh
python evidence/task-detector-2026-10-01/analyze.py
```

To reproduce [observations.json](observations.json), use the existing SITL
environment with `pyulog==1.2.4`:

```sh
python evidence/task-detector-2026-10-01/analyze.py --extract
```

The extraction retains the relevant topic fields from every logged instance,
initial timing parameters and any recorded changes to those parameters.
Input hashes refer to the original compressed logs in their existing packets.

## Limits and disposition

The logger samples telemetry status at a reduced rate, so the last publication
that refreshed Commander may be missing. Neither the exact final heartbeat
reception nor that final refresh is directly recorded. The cached injection
stamp also has no upper bound. The observed endpoint comparison therefore
does not establish an injection bound or a calibrated tolerance.

NP-3 closes with the source mechanism identified and the exact split of the
pre-detection interval recorded as a measurement limit. Historical predictions
and verdicts stay unchanged. NP-6 and the injection-bound requirement remain
open. The approved coverage gate and seeds are unchanged; these development
captures contribute no confirmation cells.

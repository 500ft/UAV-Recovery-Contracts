"""Deterministic case identity: (configuration row, event class, seed) -> one frozen case.

A case ID is the unit the runner accepts, the manifest records, and the analysis counts. It is derived, not
invented: the same matrix and the same seed list always produce the same IDs, so a case cannot be quietly
added or renamed after results exist. Decisions D4 (event classes), D5 (configurations), D12 (horizon) and
the seed list live in docs/specs/formal-composition/decisions-2026-09-19.md.
"""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / "protocols/configuration-matrix.json").read_text())
ROWS = {r["configuration_id"]: r for r in MATRIX["rows"]}

EVENT_CLASSES = ("offboard_loss", "datalink_loss", "rc_loss", "gps_loss", "battery_critical", "geofence_breach")
# Frozen classes that this rig cannot inject, with the reason. They stay in EVENT_CLASSES so the decision is
# visible rather than quietly dropped, they are excluded from the campaign, and the runner refuses them.
NOT_INJECTABLE = {
    "rc_loss": "PX4 in SIH SITL did not accept MAVLink MANUAL_CONTROL as a manual-control source in this rig "
               "(2026-09-20: manual_control_signal_lost stayed true while the stream ran at 10 Hz), so there is "
               "no RC signal to remove. Decision D13; needs a simulated RC source or a joystick bridge.",
}
INJECTABLE_CLASSES = tuple(c for c in EVENT_CLASSES if c not in NOT_INJECTABLE)
SINGLE_EVENT_SEEDS = (1, 2, 3, 5, 8)
PAIRED_SEEDS = (11, 13, 17)
# D12: horizon = injection + 45 s or terminal mode, whichever comes first.
# Decision: how long to watch after the stimulus.  [Q-HORIZON in protocols/quantities.json]
#
#   Question    How long must the observation window be before an absence of recovery is informative?
#   Inputs      COM_DL_LOSS_T = 10 s   sourced, vendor default [B10, Q-DL-LOSS-T]
#               COM_FAIL_ACT_T = 5 s   sourced, vendor default [B10, Q-FAIL-ACT-T]
#               predicted transition at +15 s after injection (timeline T1, calculated from the two above)
#   Assumption  the response is a mode change, not a completed manoeuvre. Completion is out of scope (D17), so
#               no climb, travel or descent time enters this number.
#   Model       horizon >= detection + hold delay + margin for the mode change to be logged and observed
#   Substitute  10 s + 5 s + margin;  45 s leaves 30 s beyond the predicted transition
#   Result      45 s, selected, not forced. Any value above about 20 s satisfies the model.
#   Sensitivity Too short reports a false ABSENCE of recovery, which is the exact conclusion these runs reach,
#               so the margin is deliberately large rather than tight.
#   Validation  Partial. The 2026-09-23 run held its mode for the whole horizon, so the horizon was not the
#               limiting factor in that absence. A recovery slower than 45 s has not been excluded by measurement.
HORIZON_S = 45.0
# The seed varies the injection time within +/- 2 s of the scheduled vehicle time; the offset is part of the ID.
SEED_OFFSET_S = {1: 0.0, 2: -1.0, 3: 1.0, 5: -2.0, 8: 2.0, 11: 0.0, 13: -1.5, 17: 1.5}
NOMINAL_INJECT_T_S = 40.0
# Parameters the runner must set for a specific event class to be injectable at all. They are declared here so
# the expected timelines and the tests can see them, rather than hiding as literals inside the runner.
# Parameters a flight mode needs to fly the same profile as the others. Auto Loiter climbs with the autopilot's
# own takeoff, whose altitude comes from MIS_TAKEOFF_ALT rather than from a setpoint.
PER_MODE_PARAMS = {"auto_loiter": {"MIS_TAKEOFF_ALT": 10.0}}
PER_EVENT_PARAMS = {
    "geofence_breach": {"GF_MAX_HOR_DIST": 20.0},
    "battery_critical": {"SYS_FAIL_BAT_LVL": 2},
    "battery_emergency": {"SYS_FAIL_BAT_LVL": 3},
}


def case_id(configuration_id: str, event: str, seed: int) -> str:
    return f"{configuration_id}__{event}__seed{seed}"


def resolve(configuration_id: str, event: str, seed: int, *, development_offset_s: float | None = None) -> dict:
    """The frozen case, or a ValueError naming exactly what is wrong. The runner never invents a default."""
    if configuration_id not in ROWS:
        raise ValueError(f"unknown configuration_id {configuration_id!r}; matrix has {sorted(ROWS)}")
    if event not in EVENT_CLASSES and event != "none":
        raise ValueError(f"unknown event class {event!r}; frozen classes are {list(EVENT_CLASSES)} (D4)")
    if development_offset_s is not None:
        import math
        if seed in SEED_OFFSET_S or not math.isfinite(development_offset_s) or abs(development_offset_s) > 2:
            raise ValueError("development requires a non-frozen label and a finite offset within +/-2 s")
        offset = development_offset_s
    elif seed not in SEED_OFFSET_S:
        raise ValueError(f"seed {seed} is not in the frozen seed list {sorted(SEED_OFFSET_S)}")
    else:
        offset = SEED_OFFSET_S[seed]
    row = ROWS[configuration_id]
    return dict(
        case_id=case_id(configuration_id, event, seed) if development_offset_s is None else
                f"{configuration_id}__{event}__development{seed}_offset{offset:g}",
        configuration_id=configuration_id,
        event=event,
        seed=seed,
        inject_at_vehicle_s=round(NOMINAL_INJECT_T_S + offset, 3),
        horizon_s=HORIZON_S,
        expected_action=row["realised_action_per_class"].get(event),
        firmware_commit=MATRIX["firmware"]["commit"],
        firmware_tag=MATRIX["firmware"]["tag"],
        airframe=MATRIX["vehicle"]["airframe"],
        parameters_sha256=row["parameters_sha256"],
        parameters={**MATRIX["common_params"], **row["deltas_from_defaults"]},
    )


def single_event_campaign() -> list[dict]:
    """The registered validation tier: every frozen class against the two link-loss intentions, five seeds."""
    configs = ("px4-v1.17.0-sih-quadx-rtl", "px4-v1.17.0-sih-quadx-hold")
    return [resolve(c, e, s) for e in INJECTABLE_CLASSES for c in configs for s in SINGLE_EVENT_SEEDS]

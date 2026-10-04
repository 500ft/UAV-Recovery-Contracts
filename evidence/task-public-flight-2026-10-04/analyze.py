"""Extract de-located observations from the three locally retained development logs.

Usage: python evidence/task-public-flight-2026-10-04/analyze.py CACHE_DIRECTORY
Requires pyulog for extraction. No raw log metadata, coordinates or commands are emitted.
"""
import hashlib
import importlib.metadata
import json
from pathlib import Path
import statistics
import sys

PARAMETERS = """SDLOG_PROFILE SDLOG_MODE SDLOG_BACKEND SYS_AUTOSTART COM_DL_LOSS_T
COM_FAIL_ACT_T NAV_DLL_ACT GF_ACTION GF_PREDICT COM_POS_LOW_ACT COM_POS_FS_EPH
COM_RC_LOSS_T NAV_RCL_ACT COM_RC_OVERRIDE COM_RCL_EXCEPT COM_DLL_EXCEPT
COM_LOW_BAT_ACT COM_POSCTL_NAVL COM_FLTT_LOW_ACT COM_IMB_PROP_ACT COM_OBL_RC_ACT
COM_WIND_MAX_ACT COM_FLT_TIME_MAX""".split()
FLAGS = """mode_req_angular_velocity mode_req_attitude mode_req_local_alt
mode_req_local_position mode_req_local_position_relaxed mode_req_global_position
mode_req_global_position_relaxed mode_req_mission mode_req_offboard_signal
mode_req_home_position mode_req_wind_and_flight_time_compliance mode_req_prevent_arming
mode_req_manual_control mode_req_other angular_velocity_invalid attitude_invalid
local_altitude_invalid local_position_invalid local_position_invalid_relaxed
local_velocity_invalid global_position_invalid global_position_invalid_relaxed
auto_mission_missing offboard_control_signal_lost home_position_invalid
manual_control_signal_lost gcs_connection_lost battery_warning battery_low_remaining_time
battery_unhealthy geofence_breached mission_failure vtol_fixed_wing_system_failure
wind_limit_exceeded flight_time_limit_exceeded position_accuracy_low
local_position_accuracy_low navigator_failure fd_critical_failure fd_esc_arming_failure
fd_imbalanced_prop fd_motor_failure""".split()
FIELDS = {
    "failsafe_flags": FLAGS,
    "vehicle_status": "arming_state nav_state nav_state_user_intention failsafe vehicle_type failsafe_and_user_took_over failsafe_defer_state gcs_connection_lost in_transition_mode".split(),
    "vehicle_land_detected": ["landed"],
    "navigator_status": ["nav_state", "failure"],
    "telemetry_status": ["heartbeat_type_gcs"],
    "config_overrides": ["defer_failsafes", "defer_failsafes_timeout_s"],
    "geofence_result": ["geofence_max_dist_triggered", "geofence_max_alt_triggered", "geofence_custom_fence_triggered"],
    "action_request": [], "vehicle_command": [], "event": [],
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def summarize_topic(data, fields, origin):
    """Previous/new sample brackets use adjacent samples, not adjacent changes."""
    times = [int(t) - origin for t in data["timestamp"]]
    gaps = [b - a for a, b in zip(times, times[1:])]
    if any(g < 0 for g in gaps):
        raise ValueError("non-monotonic topic timestamps")
    changes = {}
    for field in fields:
        if field not in data:
            continue
        values = data[field]
        changes[field] = []
        for i, value in enumerate(values):
            if i == 0 or value != values[i - 1]:
                row = dict(previous_sample_us=times[i - 1] if i else None,
                           first_sample_us=times[i], value=float(value) if field.endswith("_s") else int(value))
                if field == "nav_state" and "nav_state_timestamp" in data:
                    row["commit_us"] = int(data["nav_state_timestamp"][i]) - origin
                changes[field].append(row)
    return dict(samples=len(times), first_us=times[0], last_us=times[-1],
                gap_us=dict(min=min(gaps), median=statistics.median(gaps), max=max(gaps)) if gaps else None,
                changes=changes)


def extract(path):
    from pyulog import ULog
    ulog = ULog(str(path))
    topics = {f"{d.name}/{d.multi_id}": summarize_topic(d.data, FIELDS[d.name], ulog.start_timestamp)
              for d in ulog.data_list if d.name in FIELDS and len(d.data["timestamp"])}
    # Full parameter values can include identifiers, so retain them only beside the raw log.
    snapshot = dict(initial={k: dict(type="int32" if isinstance(v, int) else "float32", value=v)
                             for k, v in sorted(ulog.initial_parameters.items())},
                    changes=[dict(t_us=int(t) - ulog.start_timestamp, name=k,
                                  type="int32" if isinstance(v, int) else "float32", value=v)
                             for t, k, v in ulog.changed_parameters])
    snapshot_path = path.with_suffix(".parameters.json")
    snapshot_path.write_text(json.dumps(snapshot, indent=1, allow_nan=False) + "\n")
    build_keys = "ver_sw ver_sw_release ver_vendor_sw_release ver_hw sys_name sys_os_name sys_toolchain sys_toolchain_ver".split()
    return dict(raw_sha256=digest(path), bytes=path.stat().st_size,
                build={k: ulog.msg_info_dict.get(k) for k in build_keys}, executable_sha256=None,
                duration_us=int(ulog.last_timestamp - ulog.start_timestamp),
                parameter_count=len(ulog.initial_parameters), parameter_changes=len(ulog.changed_parameters),
                parameter_snapshot_sha256=digest(snapshot_path),
                parameter_scope="All ULog initial parameter records and changes retained locally with types. PX4 logs used parameters; completeness against the executed binary is unproven.",
                parameters={k: ulog.initial_parameters[k] for k in PARAMETERS if k in ulog.initial_parameters},
                relevant_parameter_changes=[v for v in snapshot["changes"] if v["name"] in PARAMETERS],
                dropout_records=len(ulog.dropouts),
                dropout_duration_ms=sum(int(d.duration) for d in ulog.dropouts),
                absent_topics=[name for name in FIELDS if not any(k.startswith(name + "/") for k in topics)],
                topics=topics)


def generate(cache):
    logs = {label: extract(cache / (label + ".ulg")) for label in ["candidate-a", "candidate-b", "candidate-c"]}
    geofence = logs["candidate-c"]["topics"]
    breach = next(r for r in geofence["failsafe_flags/0"]["changes"]["geofence_breached"] if r["value"] == 1)
    commits = geofence["vehicle_status/0"]["changes"]["nav_state"]
    hold = next(r for r in commits if r["value"] == 4)
    rtl = next(r for r in commits if r["value"] == 5)
    navigator = next(r for r in geofence["navigator_status/0"]["changes"]["nav_state"] if r["value"] == 5)
    manifest = json.loads((cache / "source-manifest.json").read_text())
    for entry in manifest["candidates"]:
        logs[entry["label"]]["retrieved_date"] = entry["retrieved_utc"][:10]
        assert logs[entry["label"]]["raw_sha256"] == entry["sha256"]
    exclusions = {
        "candidate-a": "Pinned source, but PX4_SITL hardware identity; no failsafe_flags topic or observed failsafe. Excluded as a public-flight event.",
        "candidate-b": "Different firmware; RC loss precedes datalink loss and remains active across it. RC is outside the admitted domain. Log starts armed; complete selector history and update inputs unavailable.",
        "candidate-c": "Different firmware; MANUAL then ALTCTL then POSCTL mode history. Geofence result topic, pre-arm selector history, per-update flags and request/override consumption are unavailable. Reconstruct sampled event only; no model replay.",
    }
    return dict(
        state="executed public-log development feasibility; incomplete observability for replay",
        extraction=dict(python=sys.version.split()[0], pyulog=importlib.metadata.version("pyulog"),
                        script_sha256=digest(Path(__file__)),
                        sources_sha256=digest(Path(__file__).with_name("sources.json"))),
        counts=dict(metadata_rows_returned={q: len(json.loads((cache / (q + "-metadata.json")).read_text())["data"])
                                           for q in ["pin", "failsafe", "geofence", "datalink", "position-loss"]},
                    attempted_downloads=3, parsed_logs=3, replay_excluded_logs=3,
                    reconstructed_events=1, model_replays=0, native_builds=0, confirmation_runs=0),
        selection_deviation="Keyword metadata pages were inspected despite available generic pin matches, to find event-labelled candidates. All three choices were recorded before parsing any ULog; all are development.",
        clock="Microseconds relative to each ULog header start, on that vehicle boot clock. Negative values are cached pre-start samples. No UTC or boot epoch is exported.",
        attribution=dict(creator="PX4", source="https://review.px4.io/", license="https://creativecommons.org/licenses/by/4.0/",
                         modifications="Allowlisted fields, relative timestamps, transition and gap summaries; raw logs and source-specific URLs retained privately."),
        exclusions=exclusions, logs=logs,
        geofence_observation=dict(
            sampled_breach_bracket_us=[breach["previous_sample_us"], breach["first_sample_us"]],
            hold_commit_us=hold["commit_us"], rtl_commit_us=rtl["commit_us"],
            hold_to_rtl_commit_us=rtl["commit_us"] - hold["commit_us"],
            logged_flag_to_hold_commit_us=hold["commit_us"] - breach["first_sample_us"],
            logged_flag_to_rtl_commit_us=rtl["commit_us"] - breach["first_sample_us"],
            sampled_flag_to_rtl_interval_us=[rtl["commit_us"] - breach["first_sample_us"],
                                            rtl["commit_us"] - breach["previous_sample_us"]],
            first_navigator_rtl_us=navigator["first_sample_us"],
            commit_to_navigator_report_us=navigator["first_sample_us"] - rtl["commit_us"],
            geometric_crossing_us=None, geofence_detector_publication_us=None,
            selected_action_update_us=None, actuator_response_us=None,
            interpretation="Bracket spans adjacent sampled flag states, not the geometric crossing. Unlogged toggles and consumed-update times are unknown. Navigator status is a mode report, not physical response. No timing pass/fail."),
        source_manifest_sha256=digest(cache / "source-manifest.json"),
        firmware_source_manifest_sha256=digest(cache / "firmware-source.json"),
        selection_registration=json.loads((cache / "selection-registration.json").read_text()),
        raw_selection_registered_utc=manifest["registered_utc"],
    )


if __name__ == "__main__":
    print(json.dumps(generate(Path(sys.argv[1])), indent=1, allow_nan=False))

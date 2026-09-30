"""Run one frozen case against pinned PX4 SIH SITL and write a manifest-backed trace (URC-04).

    python -m harness.run_case --config px4-v1.17.0-sih-quadx-rtl --event datalink_loss --seed 1 \
        --px4-build <build dir> --out evidence/<task>/runs/

Contract (week plan W3.1, with decision D6):
 1. resolve exactly one case from the frozen matrix, or exit 2;
 2. refuse a firmware commit that does not match the matrix, or exit 2;
 3. refuse an existing output directory, or exit 2;
 4. write the resolved manifest BEFORE the vehicle is launched;
 5. launch the pinned build in an isolated working directory;
 6. establish NORMAL_TRACKING (armed, at altitude, offboard tracking) before injecting;
 7. inject exactly one registered event, scheduled on VEHICLE time, not host time;
 8. capture raw telemetry, the autopilot log, and exit status;
 9. stop at the registered terminal mode or the horizon;
10. normalise and validate the trace;
11. exit 0 for a completed valid run even when the behaviour differs from the model; nonzero only for
    setup, capture or schema failure.

Baselines: GCS heartbeat 1 Hz [B5]; offboard setpoints 10 Hz, above the 2 Hz proof-of-life floor [B4];
failure injection needs SYS_FAILURE_EN [B3]; parameter defaults and timers [B10].
"""
from __future__ import annotations
import argparse, json, os, shutil, signal, struct, subprocess, sys, threading, time
from pathlib import Path

from harness.cases import resolve, MATRIX, PER_EVENT_PARAMS, PER_MODE_PARAMS
from harness.identity import file_sha256
from harness.trace import build_trace

INSTANCE = int(os.environ.get("PX4_INSTANCE", "0"))
GCS_PORT = 14550 + INSTANCE
# pymavlink is imported only once a case has been accepted, so every refusal in the contract (unknown case,
# missing binary, hash mismatch, existing directory) works in an environment without the SITL dependencies.
mavutil = mav = None


def _load_mavlink():
    global mavutil, mav
    from pymavlink import mavutil as _mavutil
    from pymavlink.dialects.v20 import common as _mav
    mavutil, mav = _mavutil, _mav


FAILURE_UNIT = {"gps": 4, "battery": 100}
FAILURE_TYPE = {"ok": 0, "off": 1, "wrong": 4}
TAKEOFF_ALT_M = 10.0
SETUP_FAILURE, CAPTURE_FAILURE = 2, 3


class Streams:
    """The three input streams the vehicle depends on. Stopping one is an injection."""

    def __init__(self, gcs):
        self.gcs = gcs
        self.heartbeat = self.setpoints = False
        self.target = [0.0, 0.0, -TAKEOFF_ALT_M]
        self._stop = False
        self.errors: list[str] = []
        threading.Thread(target=self._loop, daemon=True).start()

    def _loop(self):
        n = 0
        while not self._stop:
            try:
                if self.heartbeat and n % 10 == 0:
                    self.gcs.mav.heartbeat_send(mav.MAV_TYPE_GCS, mav.MAV_AUTOPILOT_INVALID, 0, 0, 0)
                if self.setpoints:
                    self.gcs.mav.set_position_target_local_ned_send(
                        0, 1, 1, mav.MAV_FRAME_LOCAL_NED, 0b0000111111111000, *self.target, 0, 0, 0, 0, 0, 0, 0, 0)
            except Exception as exc:  # never silent: a stream that stops sending must be visible
                self.errors.append(f"{type(exc).__name__}: {exc}")
            n += 1
            time.sleep(0.1)

    def stop(self):
        self._stop = True


class Vehicle:
    """Thin MAVLink view of the vehicle: parameters, the pre-arm gate, and vehicle-clock time."""

    def __init__(self, gcs, log):
        self.gcs, self.log = gcs, log
        self.boot_s = 0.0
        self.prearm_ok = False
        self.health = None
        self.param_types = {}

    def pump(self, timeout=1.0):
        m = self.gcs.recv_match(blocking=True, timeout=timeout)
        if m is None:
            return None
        if m.get_type() == "SYS_STATUS":
            self.health = m.onboard_control_sensors_health
            self.prearm_ok = bool(self.health & mav.MAV_SYS_STATUS_PREARM_CHECK)
        if "time_boot_ms" in m.to_dict():
            self.boot_s = m.time_boot_ms / 1000.0
        return m

    def set_param(self, name, value):
        """Send the value and move on. Confirmation is not done here: every parameter is read back afterwards
        and compared against the request in the configuration_applied stage, which is the check that matters.
        Confirming each one inline as well made the run fail on a single dropped PARAM_VALUE reply."""
        if name not in self.param_types:
            self.read_param(name)
        ptype = self.param_types[name]
        if ptype == mav.MAV_PARAM_TYPE_INT32:
            if int(value) != value:
                raise ValueError(f"integer parameter {name} cannot take {value}")
            wire = struct.unpack("<f", struct.pack("<i", int(value)))[0]
            if struct.unpack("<i", struct.pack("<f", wire))[0] != value:
                raise ValueError(f"integer parameter {name} cannot round-trip through the MAVLink float field")
        else:
            wire = float(value)
        for _ in range(3):
            self.gcs.mav.param_set_send(1, 1, name.encode(), wire, ptype)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 0.6:
                m = self.gcs.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.5)
                if m and m.param_id.rstrip("\x00") == name and abs(self.decode_param(m) - value) < 1e-4:
                    return self.decode_param(m)
        return None

    def decode_param(self, message):
        """PX4 bytewise PARAM_VALUE, for both explicit reads and broadcasts.

        Pinned mavlink_parameters.cpp send_param() memcpy's integer storage to
        the wire float. Its magnitude is never an encoding discriminator.
        """
        ptype = message.param_type
        if ptype == mav.MAV_PARAM_TYPE_INT32:
            value = struct.unpack("<i", struct.pack("<f", message.param_value))[0]
        elif ptype == mav.MAV_PARAM_TYPE_REAL32:
            value = message.param_value
        else:
            raise ValueError(f"unsupported PX4 parameter type {ptype}")
        self.param_types[message.param_id.rstrip("\x00")] = ptype
        return value

    def read_param(self, name):
        """Read the typed value, draining queued replies before the request.

        Both reply routes use the same bytewise encoding. The old magnitude
        heuristic accepted corrupted integer storage as a successful readback.
        """
        for _ in range(8):
            while self.gcs.recv_match(type="PARAM_VALUE", blocking=False):
                pass
            self.gcs.mav.param_request_read_send(1, 1, name.encode(), -1)
            t0 = time.monotonic()
            while time.monotonic() - t0 < 1.5:
                m = self.gcs.recv_match(type="PARAM_VALUE", blocking=True, timeout=1.0)
                if m and m.param_id.rstrip("\x00") == name:
                    return self.decode_param(m)
        raise RuntimeError(f"parameter {name} could not be read")

    def command(self, cmd, *params):
        p = list(params) + [0] * (7 - len(params))
        self.gcs.mav.command_long_send(1, 1, cmd, 0, *p)
        t0 = time.monotonic()
        while time.monotonic() - t0 < 3:
            m = self.gcs.recv_match(type="COMMAND_ACK", blocking=True, timeout=1)
            if m and m.command == cmd:
                self.log(dict(kind="command", cmd=cmd, params=p, result=m.result))
                return m.result
        self.log(dict(kind="command", cmd=cmd, params=p, result=None))
        return None

    def wait_prearm(self, deadline_s):
        """The pre-arm gate is the autopilot's own: with a link-loss failsafe enabled it also requires a live
        GCS connection, which is why the harness heartbeats before configuring (probe, 2026-09-20)."""
        t0 = time.monotonic()
        seen = set()
        while time.monotonic() - t0 < deadline_s:
            self.pump()
            if self.health is not None and self.health not in seen:
                seen.add(self.health)
                self.log(dict(kind="health", word=self.health, prearm=self.prearm_ok, t=round(time.monotonic() - t0, 1)))
            if self.prearm_ok:
                self.log(dict(kind="prearm", ready=True, waited_s=round(time.monotonic() - t0, 2), health=self.health))
                return True
        self.log(dict(kind="prearm", ready=False, waited_s=round(time.monotonic() - t0, 2), health=self.health))
        return False


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", required=True)
    ap.add_argument("--event", required=True)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--px4-build", required=True)
    ap.add_argument("--out", required=True, help="parent directory; the run directory is named by the case id")
    ap.add_argument("--restore-after", type=float, default=0.0, help="seconds after injection to restore the input")
    ap.add_argument("--intended-mode", choices=["offboard", "auto_loiter"], default="offboard",
                    help="the user-intended mode the vehicle flies in. Offboard needs only the setpoint stream; "
                         "auto_loiter needs neither setpoints nor manual control and is the control for the "
                         "hypothesis that action selection is suppressed specifically in Offboard.")
    ap.add_argument("--dry-run", action="store_true", help="resolve, check and write the manifest; do not launch")
    a = ap.parse_args(argv)

    try:
        from harness.cases import NOT_INJECTABLE
        if a.event in NOT_INJECTABLE:
            raise ValueError(f"{a.event} is not injectable in this rig: {NOT_INJECTABLE[a.event]}")
        case = resolve(a.config, a.event, a.seed)
    except ValueError as e:
        print(f"case refused: {e}", file=sys.stderr)
        return SETUP_FAILURE

    build = Path(a.px4_build).expanduser()
    if not a.dry_run:
        if not (build / "bin/px4").is_file():
            print(f"case refused: no PX4 binary at {build/'bin/px4'}", file=sys.stderr)
            return SETUP_FAILURE
        commit = (build.parents[1] / ".git") if (build.parents[1] / ".git").exists() else None
        if commit:
            head = subprocess.run(["git", "-C", str(build.parents[1]), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
            if head != case["firmware_commit"]:
                print(f"case refused: build is at {head[:12]}, matrix pins {case['firmware_commit'][:12]}", file=sys.stderr)
                return SETUP_FAILURE

    out = Path(a.out) / case["case_id"]
    if out.exists():
        print(f"case refused: {out} already exists; a run directory is never overwritten", file=sys.stderr)
        return SETUP_FAILURE
    out.mkdir(parents=True)
    t_start = time.monotonic()
    raw = (out / "raw.jsonl").open("w")

    stages: list[dict] = []

    def stage(name, status, evidence=None, **detail):
        stages.append(dict(stage=name, status=status, evidence=evidence, detail=detail))
        log(dict(kind="stage", stage=name, status=status, evidence=evidence, detail=detail))

    def log(d):
        d["t_host_s"] = round(time.monotonic() - t_start, 4)
        if raw.closed:      # after the capture file is closed the stage list is appended separately
            return
        raw.write(json.dumps(d) + "\n")
        raw.flush()

    # The intended mode belongs in the case, not bolted onto the manifest after normalisation: re-normalising a
    # stored Auto Loiter capture used to silently become the Offboard case (critique 2026-09-24, F2/TASK 2).
    case["intended_mode"] = a.intended_mode
    case["restore_after_s"] = float(a.restore_after)
    (out / "case.json").write_text(json.dumps(case, indent=1) + "\n")
    log(dict(kind="case_resolved", case_id=case["case_id"]))
    if a.dry_run:
        raw.close()
        print(json.dumps(dict(case_id=case["case_id"], dry_run=True, manifest=str(out / "case.json"))))
        return 0

    # A previous instance still holding the telemetry port is a setup problem, not a capture failure: refuse
    # up front rather than launch and time out waiting for a heartbeat (observed 2026-09-20, rep1).
    import socket
    probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        probe.bind(("0.0.0.0", GCS_PORT))
    except OSError as exc:
        print(f"case refused: UDP {GCS_PORT} is in use ({exc}); stop the previous instance first", file=sys.stderr)
        return SETUP_FAILURE
    finally:
        probe.close()

    _load_mavlink()
    work = out / "px4-work"
    work.mkdir()
    # Keep the source patch with the run that actually uses it. A pinned commit
    # alone does not identify the instrumented runtime (NP-8).
    source_diff = subprocess.run(["git", "-C", str(build.parents[1]), "diff", "HEAD", "--"],
                                 capture_output=True, text=True)
    if source_diff.returncode == 0 and source_diff.stdout:
        (out / "source.patch").write_text(source_diff.stdout)
    env = dict(os.environ, PX4_SIM_MODEL="sihsim_quadx", PX4_SIMULATOR="sihsim", PX4_SYS_AUTOSTART="10040")
    px4 = subprocess.Popen([str(build / "bin/px4"), "-d", str(build / "etc"), "-s", "etc/init.d-posix/rcS",
                            "-i", str(INSTANCE), "-w", str(work)],
                           cwd=build, env=env, stdout=(out / "px4.log").open("w"), stderr=subprocess.STDOUT)
    log(dict(kind="launch", pid=px4.pid, build=str(build),
             # Part of the execution identity: which binary actually flew, and how it was built (WP1).
             executable_sha256=file_sha256(build / "bin/px4"),
             build_identity=dict(target="px4_sitl_default", path=str(build),
                                 git_head=subprocess.run(["git", "-C", str(build.parents[1]), "rev-parse", "HEAD"],
                                                         capture_output=True, text=True).stdout.strip() or None,
                                 instrumentation=("unrecorded" if source_diff.returncode else
                                                  file_sha256(out / "source.patch") or "none"))))
    stage("launch", "ok", evidence=str(out / "px4.log"), pid=px4.pid)
    gcs = mavutil.mavlink_connection(f"udpin:0.0.0.0:{GCS_PORT}", source_system=255, source_component=190)
    v = Vehicle(gcs, log)
    streams = Streams(gcs)
    rc = 0
    try:
        if gcs.recv_match(type="HEARTBEAT", blocking=True, timeout=60) is None:
            raise RuntimeError("no vehicle heartbeat within 60 s")
        streams.heartbeat = True
        time.sleep(3)

        params = dict(case["parameters"], **PER_EVENT_PARAMS.get(a.event, {}), **PER_MODE_PARAMS.get(a.intended_mode, {}))
        for k, val in params.items():
            v.set_param(k, val)
        export = {k: v.read_param(k) for k in sorted(params)}
        log(dict(kind="param_export", values=export))
        # Section 12 item 4: a parameter that was written but never applied must not pass silently.
        mismatched = {k: dict(requested=params[k], readback=export[k]) for k in params
                      if abs(float(export[k]) - float(params[k])) > 1e-4}
        stage("configuration_applied", "ok" if not mismatched else "failed",
              evidence="param_export in raw.jsonl", requested=len(params), mismatched=mismatched)
        if mismatched:
            raise RuntimeError(f"parameters did not take effect: {mismatched}")

        for msg_id, interval in ((mav.MAVLINK_MSG_ID_LOCAL_POSITION_NED, 100000),
                                 (mav.MAVLINK_MSG_ID_GLOBAL_POSITION_INT, 100000),
                                 (mav.MAVLINK_MSG_ID_SYS_STATUS, 200000)):
            v.command(mav.MAV_CMD_SET_MESSAGE_INTERVAL, msg_id, interval)

        # The intended mode must be one that can run before the pre-arm gate will open: Position requires a
        # manual-control source, Offboard requires only the setpoint stream [B4]. Stream first, then select.
        if a.intended_mode == "offboard":
            streams.setpoints = True
            time.sleep(3)
            v.command(mav.MAV_CMD_DO_SET_MODE, mav.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 6, 0)
        else:  # auto_loiter: PX4 main mode 4 (AUTO), sub mode 3 (LOITER); no setpoint or manual stream needed
            v.command(mav.MAV_CMD_DO_SET_MODE, mav.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, 4, 3)
        time.sleep(2)
        if not v.wait_prearm(180):
            raise RuntimeError(f"pre-arm gate never opened; last health word {v.health}")
        armed = False
        if streams.errors:
            raise RuntimeError(f"input stream errors before arming: {streams.errors[:3]}")
        for attempt in range(10):
            if v.command(mav.MAV_CMD_COMPONENT_ARM_DISARM, 1) == mav.MAV_RESULT_ACCEPTED:
                armed = True
                break
            time.sleep(2)
        if not armed:
            raise RuntimeError("arming was refused on every attempt")
        log(dict(kind="event", name="arm", attempts=attempt + 1))
        if a.intended_mode == "auto_loiter":
            # No setpoint stream to climb on: command the autopilot's own takeoff to the same altitude.
            # param7 is an ABSOLUTE altitude. Passing the relative height puts the target below the home
            # elevation, so the autopilot considers the takeoff complete without climbing and then disarms
            # (observed 2026-09-23). NaN makes it use MIS_TAKEOFF_ALT, which PER_MODE_PARAMS sets.
            v.command(mav.MAV_CMD_NAV_TAKEOFF, 0, 0, 0, float("nan"), float("nan"), float("nan"), float("nan"))

        # NORMAL_TRACKING: hold the commanded altitude before anything is injected
        t0 = time.monotonic()
        tracking = False
        last_probe = 0.0
        best_z = 0.0
        while time.monotonic() - t0 < 90:
            m = v.pump()
            if m is not None and m.get_type() == "LOCAL_POSITION_NED":
                best_z = min(best_z, m.z)
                if m.z < -(TAKEOFF_ALT_M - 1.0) and abs(m.vz) < 0.3:
                    tracking = True
                    log(dict(kind="event", name="takeoff_complete", z=m.z, t_vehicle_s=m.time_boot_ms / 1000.0))
                    break
            # The climb is the one stage with no other record; probe it so a failure here is diagnosable.
            if time.monotonic() - t0 - last_probe > 5.0:
                last_probe = time.monotonic() - t0
                log(dict(kind="tracking_probe", best_z=round(best_z, 2), target_z=-(TAKEOFF_ALT_M - 1.0),
                         elapsed_s=round(last_probe, 1)))
        stage("normal_tracking", "ok" if tracking else "failed", evidence="takeoff_complete event")
        if not tracking:
            raise RuntimeError("normal tracking was never established")

        inject_at = v.boot_s + case["inject_at_vehicle_s"]
        log(dict(kind="schedule", inject_at_vehicle_s=round(inject_at, 3), rule="vehicle clock (D6)"))
        injected = restored = False
        terminal_since = None
        deadline = time.monotonic() + case["horizon_s"] + case["inject_at_vehicle_s"] + 60
        while time.monotonic() < deadline:
            m = v.pump()
            if m is not None:
                tp = m.get_type()
                if tp in ("HEARTBEAT", "STATUSTEXT", "SYS_STATUS", "GLOBAL_POSITION_INT", "LOCAL_POSITION_NED", "BATTERY_STATUS"):
                    d = m.to_dict()
                    d["kind"] = "msg"
                    d["src"] = m.get_srcSystem()
                    log(d)
            if not injected and v.boot_s >= inject_at and a.event != "none":
                injected = True
                if a.event == "offboard_loss":
                    streams.setpoints = False
                elif a.event == "datalink_loss":
                    streams.heartbeat = False
                elif a.event == "gps_loss":
                    v.command(mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["gps"], FAILURE_TYPE["off"], 0)
                elif a.event.startswith("battery"):
                    v.command(mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["battery"], FAILURE_TYPE["wrong"], 0)
                elif a.event == "geofence_breach":
                    streams.target = [60.0, 0.0, -TAKEOFF_ALT_M]
                surviving = dict(gcs_heartbeat=streams.heartbeat, offboard_setpoints=streams.setpoints)
                log(dict(kind="event", name="injection", event=a.event, t_vehicle_s=round(v.boot_s, 3),
                         scheduled_vehicle_s=round(inject_at, 3), streams=surviving))
                stage("injection", "ok", evidence="injection event in raw.jsonl",
                      scheduled_vehicle_s=round(inject_at, 3), observed_vehicle_s=round(v.boot_s, 3),
                      surviving_publishers=surviving)
            if injected and not restored and a.restore_after > 0 and v.boot_s >= inject_at + a.restore_after:
                restored = True
                if a.event == "offboard_loss":
                    streams.setpoints = True
                elif a.event == "datalink_loss":
                    streams.heartbeat = True
                elif a.event == "gps_loss":
                    v.command(mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["gps"], FAILURE_TYPE["ok"], 0)
                elif a.event.startswith("battery"):
                    v.command(mav.MAV_CMD_INJECT_FAILURE, FAILURE_UNIT["battery"], FAILURE_TYPE["ok"], 0)
                log(dict(kind="event", name="reconnect_event", t_vehicle_s=round(v.boot_s, 3)))
            if injected and v.boot_s >= inject_at + case["horizon_s"]:
                log(dict(kind="event", name="horizon_reached", t_vehicle_s=round(v.boot_s, 3)))
                break
            if a.event == "none" and v.boot_s >= inject_at + case["horizon_s"]:
                log(dict(kind="event", name="horizon_reached", t_vehicle_s=round(v.boot_s, 3)))
                break
    except Exception as exc:  # setup or capture failure: preserved, never retried with a different seed
        log(dict(kind="failure", error=type(exc).__name__, detail=str(exc)[:400]))
        stage("capture", "failed", evidence="failure record in raw.jsonl", error=type(exc).__name__)
        rc = CAPTURE_FAILURE
    finally:
        streams.stop()
        raw.close()
        px4.send_signal(signal.SIGINT)
        try:
            px4.wait(timeout=20)
        except subprocess.TimeoutExpired:
            px4.kill()
        logs = sorted((work / "log").rglob("*.ulg"))
        if logs:
            shutil.copy(logs[-1], out / "flight.ulg")
        if rc == 0:
            stage("capture", "ok", evidence=str(out / "raw.jsonl"), autopilot_log=bool(logs))
        with (out / "raw.jsonl").open("a") as tail:
            tail.write(json.dumps(dict(kind="stages", stages=stages)) + "\n")

    trace = build_trace(out, case, MATRIX)
    trace.setdefault("stages", []).append(dict(stage="normalization",
                                               status="ok" if trace["validity"]["valid"] else "failed",
                                               evidence=str(out / "trace.json"), detail={}))
    (out / "trace.json").write_text(json.dumps(trace, indent=1) + "\n")
    summary = dict(case_id=case["case_id"], exit=rc, valid=trace["validity"],
                   transitions=[e["detail"] for e in trace["events"] if e["name"] == "native_transition"])
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary))
    if rc == 0 and not trace["validity"]["valid"] and "schema_failure" in trace["validity"]["reasons"]:
        return CAPTURE_FAILURE
    return rc


if __name__ == "__main__":
    sys.exit(main())

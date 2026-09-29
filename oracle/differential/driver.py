"""Differential driver: the same sequence through the model and through PX4's real Failsafe class.

    python oracle/differential/driver.py model <seq> <out.csv>      run one sequence through the Python model
    python oracle/differential/driver.py compare <seq> <model.csv> <oracle.csv>
    python oracle/differential/driver.py report <dir with *.model.csv and *.oracle.csv> [--seq-dir DIR]

Layer A (the model) against layer B (the real class), on identical inputs. NOT a safety oracle: the real class is
the implementation under study. A disagreement localises a discrepancy between transcription and source; it says
nothing yet about the integrated runtime, which is layer C.

The comparison is on the TIMELINE of selected actions, because that is what both layers expose. Selected action
per update is compared exactly; the times at which the action changes are compared within one update period.
Nothing here modifies the model to make it agree.
"""
from __future__ import annotations
import csv, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from model.px4_failsafe import DEFAULTS, Selector  # noqa: E402

START_US = 5_000_000
# Real flag -> the model's hazard name.
FLAG_TO_HAZARD = {"gcs_connection_lost": "datalink_loss", "manual_control_signal_lost": "rc_loss",
                  "geofence_breached": "geofence_breach", "position_accuracy_low": "position_low"}
# PX4 numbering of actions, so both CSVs speak one language.
ACTION_NAMES = ["None", "Warn", "Fallback to PosCtrl", "Fallback to AltCtrl", "Fallback to Stabilized", "Hold",
                "RTL", "Land", "Descend", "Disarm", "Terminate"]
MODEL_TO_REAL = {"None": "None", "Warn": "Warn", "FallbackPosCtrl": "Fallback to PosCtrl",
                 "FallbackAltCtrl": "Fallback to AltCtrl", "FallbackStab": "Fallback to Stabilized",
                 "Hold": "Hold", "RTL": "RTL", "Land": "Land", "Descend": "Descend", "Disarm": "Disarm",
                 "Terminate": "Terminate"}


def parse(path: Path) -> list[tuple]:
    cmds = []
    for n, raw in enumerate(path.read_text().splitlines(), 1):
        line = raw.split("#", 1)[0].split()
        if not line:
            continue
        cmds.append((n, *line))
    return cmds


def run_model(seq: Path) -> list[dict]:
    """Interpret a sequence through the model with one stated convention: pending state changes are applied at
    the start of the next update, then the model is stepped by that update's length. The model is used as it is."""
    params = dict(DEFAULTS)
    cmds = parse(seq)
    sel = None
    flags, applied_flags = {}, {}
    mode, applied_mode = "POSCTL", "POSCTL"
    rows, t_us = [], START_US

    def emit():
        rows.append(dict(t_us=t_us, action=MODEL_TO_REAL[sel.selected]))

    def apply_pending():
        nonlocal applied_mode
        mode_changed = mode != applied_mode
        for name, hazard in FLAG_TO_HAZARD.items():
            was, now = applied_flags.get(name, 0), flags.get(name, 0)
            if now and not was and hazard not in sel.active:
                sel.raise_hazard(hazard)
            if mode_changed and not now and hazard in sel.active:
                sel.clear_hazard(hazard, mode_changed_or_disarmed=True)
            if not now and hazard == "position_low":
                sel.clear_hazard(hazard)
            applied_flags[name] = now
        applied_mode = mode

    for _n, cmd, *args in cmds:
        if cmd == "param":
            if sel is not None:
                raise SystemExit("param after construction")
            v = float(args[1])
            params[args[0]] = int(v) if float(v).is_integer() and args[0] != "COM_FAIL_ACT_T" else v
            continue
        if sel is None:
            sel = Selector(dict(params))
            sel.step(0.0)
            emit()
        if cmd == "flag":
            flags[args[0]] = int(args[1])
        elif cmd == "mode":
            mode = args[0]
        elif cmd == "armed":
            pass
        elif cmd == "run":
            dt_ms = int(args[1])
            for _ in range(round(float(args[0]) * 1000 / dt_ms)):
                t_us += dt_ms * 1000
                apply_pending()
                sel.step(dt_ms / 1000.0)
                emit()
        else:
            raise SystemExit(f"unknown command {cmd}")
    return rows


def transitions(rows: list[dict]) -> list[tuple[float, str]]:
    out, last = [], None
    for r in rows:
        if r["action"] != last:
            out.append((round((int(r["t_us"]) - START_US) / 1e6, 3), r["action"]))
            last = r["action"]
    return out


def read_csv(path: Path) -> list[dict]:
    return [dict(t_us=int(r["t_us"]), action=r["action"]) for r in csv.DictReader(path.open())]


def compare(model: list[dict], oracle: list[dict], dt_s: float) -> dict:
    n = min(len(model), len(oracle))
    mism = [i for i in range(n) if model[i]["action"] != oracle[i]["action"]]
    tm, to = transitions(model), transitions(oracle)
    aligned = len(tm) == len(to) and all(a[1] == b[1] for a, b in zip(tm, to))
    shifts = [round(b[0] - a[0], 3) for a, b in zip(tm, to)] if aligned else None
    return dict(
        updates_model=len(model), updates_oracle=len(oracle), same_length=len(model) == len(oracle),
        action_mismatch_updates=len(mism), first_mismatch_t_s=None if not mism else round((model[mism[0]]["t_us"] - START_US) / 1e6, 3),
        model_transitions=tm, oracle_transitions=to, same_transition_sequence=aligned,
        oracle_minus_model_shift_s=shifts,
        agree_within_one_update=bool(aligned and all(abs(s) <= dt_s + 1e-9 for s in shifts)),
        agree_exactly=bool(len(model) == len(oracle) and not mism))


def dt_of(seq: Path) -> float:
    return min(int(c[3]) for c in parse(seq) if c[1] == "run") / 1000.0


def main(argv: list[str]) -> int:
    if argv[:1] == ["model"]:
        rows = run_model(Path(argv[1]))
        with open(argv[2], "w", newline="") as f:
            w = csv.writer(f); w.writerow(["t_us", "action"])
            w.writerows((r["t_us"], r["action"]) for r in rows)
        return 0
    if argv[:1] == ["compare"]:
        seq = Path(argv[1])
        print(json.dumps(compare(read_csv(Path(argv[2])), read_csv(Path(argv[3])), dt_of(seq)), indent=1))
        return 0
    if argv[:1] == ["report"]:
        d = Path(argv[1])
        seq_dir = Path(argv[argv.index("--seq-dir") + 1]) if "--seq-dir" in argv else Path(__file__).parent / "sequences"
        out = {}
        for seq in sorted(seq_dir.glob("*.seq")):
            mp, op = d / f"{seq.stem}.model.csv", d / f"{seq.stem}.oracle.csv"
            if not mp.exists():
                out[seq.stem] = dict(status="not_run", reason="no model output")
            elif not op.exists():
                out[seq.stem] = dict(status="oracle_missing", reason="the real class produced no output for this sequence")
            else:
                out[seq.stem] = compare(read_csv(mp), read_csv(op), dt_of(seq))
        print(json.dumps(out, indent=1))
        return 0
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

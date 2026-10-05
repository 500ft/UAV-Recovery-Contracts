#!/usr/bin/env python3
"""Re-check the declared-domain campaign record (evidence/task-domain-2026-10-03).

Checks that anyone can run from the repository:
  1. the corpus regenerates from its seeds to the registered manifest hash;
  2. the committed model and driver match the verification-freeze hashes;
  3. the disagreement index accounts for every development disagreement;
  4. development and reserved inputs are disjoint, and reserved agreement is complete.
With the raw archive present (path from archive.json), it also checks the
archive hash and that every reserved output was written after the freeze.

Run: python scripts/audit_domain_campaign.py [--archive PATH]
"""
import argparse, csv, datetime, hashlib, json, subprocess, sys, tarfile, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EV = ROOT / "evidence/task-domain-2026-10-03"
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", help="raw archive path; defaults to the one named in archive.json")
    args = ap.parse_args()
    reg = json.loads((EV / "registration.json").read_text())
    freeze = json.loads((EV / "verification-freeze.json").read_text())
    res = json.loads((EV / "results.json").read_text())
    checks = []

    with tempfile.TemporaryDirectory() as d:
        subprocess.run([sys.executable, str(ROOT / "oracle/differential/campaign.py"), "generate",
                        str(EV / "campaign.json"), f"{d}/corpus"], check=True, capture_output=True)
        checks.append(("corpus regenerates to the registered manifest hash",
                       sha(f"{d}/corpus/manifest.json") == reg["corpus_manifest_sha256"]))

    checks.append(("model matches the freeze hash", sha(ROOT / "model/px4_failsafe.py") == freeze["model_sha256"]))
    checks.append(("driver matches the freeze hash", sha(ROOT / "oracle/differential/driver.py") == freeze["driver_sha256"]))

    rows = list(csv.DictReader(open(EV / "development-disagreements.csv")))
    expected = res["before"]["directed"]["all"]["disagree"] + res["before"]["development"]["all"]["disagree"]
    checks.append((f"disagreement index has every failure ({len(rows)} rows, {expected} expected)", len(rows) == expected))
    checks.append(("every indexed failure resolved in development", all(r["resolved_in_development"] == "True" for r in rows)))
    dup = res["duplicate_inputs"]
    checks.append(("development and reserved inputs disjoint", sum(dup.values()) == 0))
    r = res["reserved"]["all"]
    checks.append((f"reserved agreement {r['agree']}/{r['executed']}", r["agree"] == r["executed"] and r["excluded"] == 0))

    archive = Path(args.archive or json.loads((EV / "archive.json").read_text())["path"])
    if archive.is_file():
        checks.append(("raw archive hash matches archive.json", sha(archive) == json.loads((EV / "archive.json").read_text())["sha256"]))
        fz = datetime.datetime.fromisoformat(freeze["recorded_before_reserved_execution_utc"]).timestamp()
        outs = [m.mtime for m in tarfile.open(archive).getmembers()
                if m.isfile() and "reserved" in m.name.lower() and not m.name.endswith(".seq")]
        # archive mtimes are whole seconds; the freeze record has sub-second precision
        checks.append((f"all {len(outs)} reserved outputs written at or after the freeze", bool(outs) and min(outs) >= int(fz)))
    else:
        print(f"(raw archive not present at {archive}; time-order checks skipped)")

    for name, ok in checks:
        print(("PASS " if ok else "FAIL ") + name)
    return 0 if all(ok for _, ok in checks) else 1


if __name__ == "__main__":
    sys.exit(main())

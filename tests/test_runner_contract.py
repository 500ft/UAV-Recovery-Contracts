"""URC-04 runner contract, exercised offline. No test in this file launches PX4 or touches the network."""
import json, subprocess, sys, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness import cases  # noqa: E402

SETUP_FAILURE = 2


def run(args):
    return subprocess.run([sys.executable, "-m", "harness.run_case"] + args, cwd=ROOT, capture_output=True, text=True)


class CaseResolutionTests(unittest.TestCase):
    def test_resolution_refuses_anything_not_frozen(self):
        for kwargs in (dict(configuration_id="no-such-config", event="datalink_loss", seed=1),
                       dict(configuration_id="px4-v1.17.0-sih-quadx-rtl", event="alien_ray", seed=1),
                       dict(configuration_id="px4-v1.17.0-sih-quadx-rtl", event="datalink_loss", seed=4)):
            with self.subTest(**kwargs), self.assertRaises(ValueError):
                cases.resolve(**kwargs)

    def test_non_injectable_class_remains_documented(self):
        self.assertIn("rc_loss", cases.EVENT_CLASSES)
        self.assertIn("rc_loss", cases.NOT_INJECTABLE)
        self.assertTrue(cases.NOT_INJECTABLE["rc_loss"].strip())

    def test_runner_refuses_a_non_injectable_class_with_the_reason(self):
        import tempfile as _tf
        with _tf.TemporaryDirectory() as d:
            r = run(["--config", "px4-v1.17.0-sih-quadx-rtl", "--event", "rc_loss", "--seed", "1",
                     "--px4-build", "/nonexistent", "--out", d, "--dry-run"])
            self.assertEqual(r.returncode, SETUP_FAILURE)
            self.assertIn("not injectable", r.stderr)

    def test_case_carries_the_pinned_identity_and_expected_action(self):
        c = cases.resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1)
        self.assertRegex(c["firmware_commit"], r"^[0-9a-f]{40}$")
        self.assertEqual(c["expected_action"], "RTL")
        self.assertEqual(c["parameters"]["SYS_FAILURE_EN"], 1)
        self.assertAlmostEqual(c["inject_at_vehicle_s"], cases.NOMINAL_INJECT_T_S)

    def test_seed_changes_only_the_injection_time(self):
        a = cases.resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1)
        b = cases.resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 5)
        self.assertNotEqual(a["inject_at_vehicle_s"], b["inject_at_vehicle_s"])
        self.assertEqual({k: v for k, v in a.items() if k not in ("case_id", "seed", "inject_at_vehicle_s")},
                         {k: v for k, v in b.items() if k not in ("case_id", "seed", "inject_at_vehicle_s")})


class RunnerContractTests(unittest.TestCase):
    def test_unknown_case_is_refused_before_anything_is_created(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(["--config", "nope", "--event", "datalink_loss", "--seed", "1", "--px4-build", "/nonexistent", "--out", d, "--dry-run"])
            self.assertEqual(r.returncode, SETUP_FAILURE)
            self.assertIn("case refused", r.stderr)
            self.assertEqual(list(Path(d).iterdir()), [])

    def test_missing_px4_binary_is_refused(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(["--config", "px4-v1.17.0-sih-quadx-rtl", "--event", "datalink_loss", "--seed", "1",
                     "--px4-build", str(Path(d) / "absent"), "--out", d])
            self.assertEqual(r.returncode, SETUP_FAILURE)
            self.assertIn("no PX4 binary", r.stderr)

    def test_existing_run_directory_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            case_dir = Path(d) / cases.case_id("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1)
            case_dir.mkdir()
            (case_dir / "precious.json").write_text("{}")
            r = run(["--config", "px4-v1.17.0-sih-quadx-rtl", "--event", "datalink_loss", "--seed", "1",
                     "--px4-build", "/nonexistent", "--out", d, "--dry-run"])
            self.assertEqual(r.returncode, SETUP_FAILURE)
            self.assertIn("already exists", r.stderr)
            self.assertTrue((case_dir / "precious.json").exists())

    def test_dry_run_writes_the_manifest_before_any_launch(self):
        with tempfile.TemporaryDirectory() as d:
            r = run(["--config", "px4-v1.17.0-sih-quadx-rtl", "--event", "datalink_loss", "--seed", "1",
                     "--px4-build", "/nonexistent", "--out", d, "--dry-run"])
            self.assertEqual(r.returncode, 0, r.stderr)
            case_file = Path(d) / cases.case_id("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1) / "case.json"
            self.assertTrue(case_file.is_file())
            self.assertEqual(json.loads(case_file.read_text())["expected_action"], "RTL")
            self.assertFalse((case_file.parent / "px4-work").exists())


if __name__ == "__main__":
    unittest.main()

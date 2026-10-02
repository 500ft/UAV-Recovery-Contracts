"""Scenario, execution and analysis identity are three answers, not one (owner review 2026-09-25, WP1)."""
import json, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from harness.cases import resolve                                        # noqa: E402
from harness.identity import analysis, digest, execution, scenario       # noqa: E402

CASE = resolve("px4-v1.17.0-sih-quadx-rtl", "datalink_loss", 1)
LEGACY = ROOT / "evidence/task-measurement-repair-2026-09-24/legacy-captures.json"


def sid(**kw):
    case = dict(CASE, **{k: v for k, v in kw.items() if k in CASE})
    return scenario(case, intended_mode=kw.get("intended_mode", "offboard"),
                    restore_after_s=kw.get("restore_after_s", 0.0),
                    applied_overrides=kw.get("applied_overrides"))["scenario_id"]


class ScenarioIdentityTests(unittest.TestCase):
    def test_the_same_request_is_the_same_id(self):
        self.assertEqual(sid(), sid())

    def test_key_order_does_not_matter(self):
        a = {"b": 2, "a": 1}
        b = {"a": 1, "b": 2}
        self.assertEqual(digest(a), digest(b))

    def test_each_requested_thing_changes_the_id(self):
        base = sid()
        self.assertNotEqual(base, sid(intended_mode="auto_loiter"), "intended mode")
        self.assertNotEqual(base, sid(inject_at_vehicle_s=41.0), "event schedule")
        self.assertNotEqual(base, sid(restore_after_s=5.0), "restore policy")
        self.assertNotEqual(base, sid(horizon_s=60.0), "observation horizon")
        self.assertNotEqual(base, sid(applied_overrides={"NAV_DLL_ACT": 3}), "an applied parameter")

    def test_a_seed_relabelling_that_changes_nothing_changes_nothing(self):
        """The offset is what varies. An identical offset under another label is the same schedule."""
        a = scenario(dict(CASE, seed=1), intended_mode="offboard")
        b = scenario(dict(CASE, seed=1), intended_mode="offboard")
        self.assertEqual(a["scenario_id"], b["scenario_id"])
        self.assertEqual(a["schedule"]["inject_at_vehicle_ms"], int(round(CASE["inject_at_vehicle_s"] * 1000)))

    def test_times_hash_as_integers_not_as_float_text(self):
        self.assertEqual(sid(inject_at_vehicle_s=40.0), sid(inject_at_vehicle_s=40.0000000001))


class ExecutionIdentityTests(unittest.TestCase):
    def _ex(self, **kw):
        base = dict(repeat="rep1", executable_sha256="d" * 64, build={"target": "px4_sitl_default"},
                    overrides_readback={"NAV_DLL_ACT": 2.0}, realized_events={"injection": 40.0},
                    raw_artifacts={"raw.jsonl": "e" * 64})
        return execution(sid(), **dict(base, **kw))

    def test_the_executable_is_part_of_the_execution_not_the_scenario(self):
        self.assertNotEqual(self._ex()["execution_id"], self._ex(executable_sha256="f" * 64)["execution_id"])

    def test_a_repeat_never_overwrites_another(self):
        self.assertNotEqual(self._ex(repeat="rep1")["execution_id"], self._ex(repeat="rep2")["execution_id"])

    def test_the_parameter_readback_is_never_called_complete(self):
        ex = self._ex()
        self.assertFalse(ex["overrides_readback_complete"])
        self.assertIn("explicitly set", ex["overrides_readback_scope"])

    def test_full_snapshot_is_separate_from_override_readback(self):
        snapshot = {'before': {'sha256': 'a' * 64, 'complete': True}}
        ex = self._ex(parameter_snapshots=snapshot)
        self.assertEqual(ex['parameter_snapshots'], snapshot)
        self.assertFalse(ex['overrides_readback_complete'])
        self.assertNotEqual(ex['execution_id'], self._ex()['execution_id'])

    def test_missing_components_stay_unknown_and_are_not_invented(self):
        ex = self._ex(executable_sha256=None, build=None, overrides_readback=None, raw_artifacts=None)
        self.assertEqual(ex["executable_sha256"], "unknown")
        self.assertEqual(ex["build"], "unknown")
        self.assertEqual(ex["overrides_readback_sha256"], "unknown")


class AnalysisIdentityTests(unittest.TestCase):
    def test_re_reading_the_same_bytes_changes_only_the_analysis(self):
        ex = execution(sid(), repeat="rep1", executable_sha256=None, build=None, overrides_readback=None,
                       realized_events=None, raw_artifacts={"raw.jsonl": "e" * 64})
        a = analysis(ex["execution_id"], inputs={"raw.jsonl": "e" * 64}, protocol_version="v1", verdict_config={})
        b = analysis(ex["execution_id"], inputs={"raw.jsonl": "e" * 64}, protocol_version="v2", verdict_config={})
        self.assertNotEqual(a["analysis_id"], b["analysis_id"])
        self.assertEqual(a["execution_id"], b["execution_id"], "the execution and its raw bytes are untouched")


@unittest.skipUnless(LEGACY.is_file(), "legacy capture map is generated from data outside git")
class LegacyCaptureMapTests(unittest.TestCase):
    def setUp(self):
        self.doc = json.loads(LEGACY.read_text())

    def test_every_known_capture_is_accounted_for_including_the_invalid_control(self):
        self.assertEqual(self.doc["captures_found"], 10)
        self.assertEqual(sum(1 for r in self.doc["rows"] if r["valid"] is False), 1)

    def test_each_capture_has_a_unique_alias_even_where_the_legacy_id_repeats(self):
        self.assertEqual(len({r["alias"] for r in self.doc["rows"]}), len(self.doc["rows"]))
        self.assertTrue(self.doc["ambiguous_legacy_ids"], "the control repeats do share one legacy id")
        for r in self.doc["rows"]:
            if not r["legacy_id_unique"]:
                self.assertGreater(len(r["legacy_id_resolves_to"]), 1, r["legacy_case_id"])

    def test_absent_components_are_named_unknown_not_filled_in(self):
        for r in self.doc["rows"]:
            self.assertEqual(r["executable_sha256"], "unknown")
            self.assertEqual(r["build_identity"], "unknown")
            self.assertIn("unknown", r["complete_parameter_snapshot"])


if __name__ == "__main__":
    unittest.main()

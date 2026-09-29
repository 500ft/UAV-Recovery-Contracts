"""The canonical register is real: every value in it matches the code that uses it, and its claims are typed.

The register exists so one number cannot drift into two values. A test that only checked the register's shape
would not catch that, so this file reads the actual code and data and compares.
"""
import ast, json, re, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
REG = json.loads((ROOT / "protocols/quantities.json").read_text())
BY_ID = {q["id"]: q for q in REG["quantities"]}


def literal(module: str, name: str):
    """Read a module-level constant without importing the module."""
    tree = ast.parse((ROOT / module).read_text())
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"{name} not found in {module}")


class RegisterShapeTests(unittest.TestCase):
    FIELDS = ("id", "name", "value", "unit", "provenance", "evidence_status", "defined_in", "used_by",
              "rationale", "what_it_is_not", "depends_on", "sensitivity", "validation")

    def test_every_quantity_is_fully_typed(self):
        for q in REG["quantities"]:
            for f in self.FIELDS:
                self.assertIn(f, q, q["id"])
                if f not in ("value", "depends_on"):
                    self.assertTrue(str(q[f]).strip(), (q["id"], f))
            self.assertIn(q["provenance"], REG["provenance"], q["id"])
            self.assertIn(q["evidence_status"], REG["evidence_status"], q["id"])

    def test_ids_are_unique_and_dependencies_resolve(self):
        self.assertEqual(len(BY_ID), len(REG["quantities"]))
        for q in REG["quantities"]:
            for dep in q["depends_on"]:
                self.assertIn(dep, BY_ID, f"{q['id']} depends on an unregistered quantity")

    def test_a_sourced_quantity_carries_a_locator(self):
        for q in REG["quantities"]:
            if q["provenance"] == "sourced":
                self.assertTrue(q.get("locator", "").strip(), q["id"])

    def test_a_calculation_is_never_described_as_a_measurement(self):
        """The distinction the whole register exists to protect."""
        for q in REG["quantities"]:
            if q["provenance"] in ("calculated", "selected", "provisional"):
                self.assertNotEqual(q["evidence_status"], "observed", q["id"])

    def test_an_unresolved_quantity_has_no_value(self):
        for q in REG["quantities"]:
            if q["evidence_status"] == "unresolved":
                self.assertIsNone(q["value"], f"{q['id']} claims a value it does not have")

    def test_a_measured_result_states_its_sample_size(self):
        for q in REG["quantities"]:
            if q["provenance"] == "measured_result" and q["evidence_status"] == "observed":
                self.assertIn("sample_size", q, q["id"])


class RegisterMatchesTheCodeTests(unittest.TestCase):
    """If these drift apart, the register is decoration."""

    def test_tolerance(self):
        tol = json.loads((ROOT / "protocols/expected-timelines.json").read_text())["tolerance"]["value_s"]
        self.assertEqual(BY_ID["Q-TOL"]["value"], tol)

    def test_horizon_and_injection_time(self):
        self.assertEqual(BY_ID["Q-HORIZON"]["value"], literal("harness/cases.py", "HORIZON_S"))
        self.assertEqual(BY_ID["Q-INJECT-T"]["value"], literal("harness/cases.py", "NOMINAL_INJECT_T_S"))

    def test_seed_offsets(self):
        offsets = sorted(set(literal("harness/cases.py", "SEED_OFFSET_S").values()))
        self.assertEqual(sorted(BY_ID["Q-SEED-OFFSETS"]["value"]), offsets)

    def test_cohort_minimum_and_title_threshold(self):
        self.assertEqual(BY_ID["Q-COHORT-MIN"]["value"], literal("harness/reproducibility.py", "MIN_COHORT"))
        self.assertEqual(BY_ID["Q-TITLE-SIM"]["value"], literal("literature/audit_identity.py", "SIMILAR"))

    def test_takeoff_altitude(self):
        self.assertEqual(BY_ID["Q-TAKEOFF-ALT"]["value"], literal("harness/run_case.py", "TAKEOFF_ALT_M"))

    def test_u3_window(self):
        props = {p["id"]: p for p in json.loads((ROOT / "protocols/unsafe-composition-properties.json").read_text())["properties"]}
        self.assertEqual(BY_ID["Q-U3-WINDOW"]["value"], props["U3"]["window_s"])

    def test_heartbeat_gap_is_the_value_the_normaliser_uses(self):
        src = (ROOT / "harness/trace.py").read_text()
        m = re.search(r"if any\(b - a > ([0-9.]+) for a, b in zip\(hb_t", src)
        self.assertIsNotNone(m, "the heartbeat-gap check moved; update the register reference")
        self.assertEqual(BY_ID["Q-HB-GAP"]["value"], float(m.group(1)))

    def test_oracle_budget(self):
        wf = (ROOT / ".github/workflows/oracle.yml").read_text()
        m = re.search(r"timeout-minutes: (\d+)", wf)
        self.assertEqual(BY_ID["Q-ORACLE-BUDGET"]["value"], int(m.group(1)))

    def test_the_delay_recharge_rate_matches_the_model(self):
        src = (ROOT / "model/px4_failsafe.py").read_text()
        self.assertIn("dt_us // 4", src, "the recharge divisor moved away from the pinned source's dt/4 (integer division)")
        self.assertEqual(BY_ID["Q-RECHARGE"]["value"], 0.25)

    def test_the_repeat_range_is_not_used_as_an_input_anywhere(self):
        """Q-REPEAT-NEW is reported, never consumed. If it gains a consumer, the tolerance argument changes."""
        self.assertIn("nothing", str(BY_ID["Q-REPEAT-NEW"]["used_by"]).lower())
        for path in ("harness/verify.py", "harness/trace.py", "harness/reproducibility.py"):
            self.assertNotIn("0.352", (ROOT / path).read_text(), path)


if __name__ == "__main__":
    unittest.main()

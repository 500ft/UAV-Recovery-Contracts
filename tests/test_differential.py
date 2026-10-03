"""The model must keep agreeing with what PX4's REAL Failsafe class did on the recorded sequences.

The records include the original CI corpus (evidence/task-differential-2026-09-29)
and later local native runs (evidence/task-armed-* and evidence/task-domain-*).
It does not depend on the model, so this is an offline regression against real behaviour, not a model checking
itself. It does NOT re-run the C++ class: that needs the pinned build, and the recorded binary hash says which.
"""
import json, sys, unittest
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "oracle/differential"))
import driver  # noqa: E402
import campaign  # noqa: E402

SEQ = ROOT / "oracle/differential/sequences"
REC = ROOT / "evidence/task-differential-2026-09-29"
ORACLE = REC / "second-run/oracle"


class DifferentialAgainstRecordedRealClassTests(unittest.TestCase):
    def test_every_sequence_has_a_recorded_real_output_and_none_is_orphaned(self):
        seqs = {p.stem for p in SEQ.glob("*.seq")}
        recorded = {p.name.removesuffix(".oracle.csv") for p in ORACLE.glob("*.oracle.csv")}
        self.assertEqual(seqs, recorded)

    def test_the_model_reproduces_the_real_class_exactly_on_every_sequence(self):
        for seq in sorted(SEQ.glob("*.seq")):
            model = driver.run_model(seq)
            real = driver.read_csv(ORACLE / f"{seq.stem}.oracle.csv")
            c = driver.compare(model, real, driver.dt_of(seq))
            self.assertTrue(c["agree_exactly"], (seq.stem, c["model_transitions"], c["oracle_transitions"]))

    def test_the_recorded_outputs_are_real_runs_not_empty_files(self):
        for csv in ORACLE.glob("*.oracle.csv"):
            rows = driver.read_csv(csv)
            self.assertGreater(len(rows), 50, csv.name)
            self.assertGreaterEqual(len(driver.transitions(rows)), 1, csv.name)

    def test_the_sequences_discriminate_they_are_not_all_trivially_none(self):
        """A differential that every implementation passes proves nothing. These must distinguish behaviours."""
        real = {p.stem: driver.transitions(driver.read_csv(ORACLE / f"{p.stem}.oracle.csv")) for p in SEQ.glob("*.seq")}
        self.assertEqual([a for _t, a in real["s1_disabled_stays_disabled.seq".removesuffix(".seq")]], ["None"])
        self.assertIn("RTL", [a for _t, a in real["s2_delayed_response_waits"]])
        self.assertNotIn("Hold", [a for _t, a in real["s3_zero_delay_removes_wait"]])
        self.assertNotIn("Hold", [a for _t, a in real["s8_delay_below_threshold"]])
        self.assertIn("Hold", [a for _t, a in real["s9_delay_above_threshold"]])

    def test_a_shorter_second_delay_is_a_real_behaviour_not_a_model_artefact(self):
        """The mechanism the interaction study targets, read off the REAL class: episode 2 acts sooner than 1."""
        rows = driver.transitions(driver.read_csv(ORACLE / "s4_short_gap_reraise.oracle.csv"))
        holds = [t for t, a in rows if a == "Hold"]
        rtls = [t for t, a in rows if a == "RTL"]
        # The first episode is cleared at 3.2 s while still in Hold, so RTL happens only in the second.
        self.assertEqual((len(holds), len(rtls)), (2, 1), rows)
        configured, second = 5.0, rtls[0] - holds[1]
        self.assertLess(second, configured - 2.0, "the second episode must act more than 2 s sooner than a fresh 5 s")
        self.assertGreater(second, 0.0)

    def test_the_first_run_that_found_the_bug_is_preserved_and_shows_it(self):
        """The historical record: 2 of the then-9 sequences disagreed by one update. Kept, not tidied away."""
        first = json.loads((REC / "first-run-before-model-fix/report.json").read_text())
        bad = sorted(k for k, v in first.items() if not v["agree_exactly"])
        self.assertEqual(bad, ["s4_short_gap_reraise", "s4b_short_gap_reraise_10ms"])
        for k in bad:
            self.assertTrue(first[k]["agree_within_one_update"], k)


class ArmedStateDifferentialTests(unittest.TestCase):
    sequences = ROOT / "oracle/differential/armed-sequences"
    evidence = ROOT / "evidence/task-armed-2026-10-03"

    def test_armed_cases_against_executed_native_outputs(self):
        for seq in sorted(self.sequences.glob("*.seq")):
            with self.subTest(sequence=seq.stem):
                real = driver.read_csv(self.evidence / "after" / f"{seq.stem}.oracle.csv")
                self.assertGreater(len(real), 1)
                model = driver.run_model(seq)
                if seq.stem == "position-disarm-rearm":
                    # Preserve task 1's mismatch; task 2 repairs mode eligibility.
                    recorded = driver.read_csv(self.evidence / "after" / f"{seq.stem}.model.csv")
                    self.assertEqual({r["action"] for r in real}, {"None"})
                    self.assertEqual({r["action"] for r in recorded}, {"None", "Hold"})
                    self.assertFalse(driver.compare(recorded, real, driver.dt_of(seq))["agree_exactly"])
                self.assertEqual(model, real)

    def test_original_sequences_against_fresh_native_outputs(self):
        for seq in sorted(SEQ.glob("*.seq")):
            with self.subTest(sequence=seq.stem):
                real = driver.read_csv(self.evidence / "after" / f"{seq.stem}.oracle.csv")
                self.assertEqual(driver.run_model(seq), real)

    def test_pre_fix_audit_and_mode_counterexample_are_preserved(self):
        before = json.loads((self.evidence / "before/report.json").read_text())
        self.assertTrue(before["audit-armed"]["agree_exactly"])
        self.assertFalse(before["audit-disarmed"]["agree_exactly"])
        after = json.loads((self.evidence / "after/report.json").read_text())
        corpus = {seq.stem for directory in (SEQ, self.sequences) for seq in directory.glob("*.seq")}
        self.assertEqual(set(after), corpus)
        self.assertEqual({name for name, result in after.items() if not result["agree_exactly"]},
                         {"position-disarm-rearm"})

    def test_unknown_command_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            seq = Path(tmp) / "unknown.seq"
            seq.write_text("unknown_command\n")
            with self.assertRaisesRegex(SystemExit, "unknown command unknown_command"):
                driver.run_model(seq)


class DeclaredDomainDifferentialTests(unittest.TestCase):
    evidence = ROOT / "evidence/task-domain-2026-10-03"

    def test_minimized_model_and_adapter_defects_against_native(self):
        for seq in sorted((self.evidence / "counterexamples").glob("*.seq")):
            with self.subTest(sequence=seq.stem):
                native = driver.read_csv(seq.with_suffix(".oracle.csv"))
                before = driver.read_csv(seq.with_suffix(".before.model.csv"))
                self.assertNotEqual(before, native)
                self.assertEqual(driver.run_model(seq), native)

    def test_reserved_representatives_against_native(self):
        for seq in sorted((self.evidence / "reserved-examples").glob("*.seq")):
            with self.subTest(sequence=seq.stem):
                self.assertEqual(driver.run_model(seq), driver.read_csv(seq.with_suffix(".oracle.csv")))

    def test_campaign_exclusions_are_rejected_before_either_adapter(self):
        cfg = json.loads((self.evidence / "campaign.json").read_text())
        for seq in (self.evidence / "excluded-probes").glob("*.seq"):
            with self.subTest(sequence=seq.stem):
                self.assertIsNotNone(campaign.admit(seq, cfg))
        for seq in (self.evidence / "counterexamples").glob("*.seq"):
            self.assertIsNone(campaign.admit(seq, cfg), seq.name)


if __name__ == "__main__":
    unittest.main()

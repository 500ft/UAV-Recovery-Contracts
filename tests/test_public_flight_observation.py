"""Sample brackets must preserve gaps and use the vehicle's mode commit stamp."""
from pathlib import Path
import runpy
import unittest


class PublicFlightObservationTests(unittest.TestCase):
    def test_adjacent_sample_bracket_commit_clock_and_allowlist(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                                   "evidence/task-public-flight-2026-10-04/analyze.py"))
        summarize = module["summarize_topic"]
        actual = summarize({"timestamp": [90, 100, 120, 180],
                            "nav_state": [1, 1, 1, 4],
                            "nav_state_timestamp": [80, 80, 80, 170],
                            "private_coordinate": [1, 2, 3, 4]}, ["nav_state"], 100)
        self.assertEqual(actual["gap_us"], {"min": 10, "median": 20, "max": 60})
        self.assertEqual(actual["changes"], {"nav_state": [
            {"previous_sample_us": None, "first_sample_us": -10, "value": 1, "commit_us": -20},
            {"previous_sample_us": 20, "first_sample_us": 80, "value": 4, "commit_us": 70},
        ]})
        with self.assertRaisesRegex(ValueError, "non-monotonic"):
            summarize({"timestamp": [20, 10]}, [], 0)


if __name__ == "__main__":
    unittest.main()

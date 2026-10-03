"""The failed instrumented attempt stays visible beside its successful control."""
import gzip
import hashlib
import json
from pathlib import Path
import runpy
import unittest

PACKET = Path(__file__).resolve().parents[1] / 'evidence/task-timing-2026-10-03'


class TimingEvidenceTests(unittest.TestCase):
    def test_attempts_and_observable_limits_are_preserved(self):
        actual = runpy.run_path(str(PACKET / 'analyze.py'))['generate']()
        self.assertEqual(actual, json.loads((PACKET / 'results.json').read_text()))
        failed, control = actual['runs']['dev101'], actual['runs']['original-control']
        self.assertIsNone(failed['injection_cached_vehicle_s'])
        self.assertFalse(failed['summary']['valid']['valid'])
        self.assertTrue(control['summary']['valid']['valid'])
        self.assertNotEqual(failed['binary_sha256'], control['binary_sha256'])
        self.assertEqual(actual['parameter_value_differences'], [])
        self.assertFalse(actual['timing_pass_fail_enabled'])
        self.assertIsNone(actual['calibrated_tolerance_s'])
        self.assertIsNone(control['timing']['last_qualifying_heartbeat_us'])
        self.assertIsNone(control['timing']['selected_action_us'])
        self.assertEqual(actual['instrumented_injections'], 0)
        for run in actual['runs']:
            snapshot = json.loads(gzip.decompress((PACKET / 'runs' / run / 'parameters-full.json.gz').read_bytes()))
            self.assertTrue(snapshot['complete'])
            self.assertEqual(len(snapshot['parameters']), actual['runs'][run]['parameter_count'])
            self.assertEqual(snapshot['parameters']['NAV_DLL_ACT']['wire_hex'], '02000000')
        registration = json.loads((PACKET / 'registration.json').read_text())
        self.assertEqual(registration['design_sha256'], hashlib.sha256((PACKET / 'design.md').read_bytes()).hexdigest())

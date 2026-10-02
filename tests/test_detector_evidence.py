"""The detector diagnosis reproduces from retained development observations."""
import hashlib
import json
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'evidence/task-detector-2026-10-01'


class DetectorEvidenceTests(unittest.TestCase):
    def test_retained_timing_diagnosis(self):
        result = runpy.run_path(str(PACKET / 'analyze.py'))['generate']()
        self.assertEqual(result, json.loads((PACKET / 'results.json').read_text()))
        for name, digest in result['input_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest)
        for run in result['runs'].values():
            self.assertTrue(run['links'])
            self.assertTrue(all(link['loss_between_logged_endpoints_plus_timeout'] for link in run['links']))
            self.assertEqual(run['timing_parameter_changes'], [])
            self.assertIsNone(run['exact_last_received_heartbeat_us'])
            self.assertIsNone(run['exact_last_commander_timer_refresh_us'])
            self.assertTrue(run['timing_verdict'].startswith('inconclusive'))
        native = result['runs']['corrected-instrumented']
        self.assertLess(native['native_consumed_flag_to_selected_rtl_us'], native['status_loss_to_rtl_us'])


if __name__ == '__main__':
    unittest.main()

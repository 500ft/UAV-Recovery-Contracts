"""Complete snapshots must cover the running firmware's entire parameter table."""
import hashlib
import json
from pathlib import Path
import tempfile
import runpy
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from harness.run_case import capture_parameters


INVENTORY = 'Symbols: x = used, + = saved, * = unsaved\nx + USED [0,0] : 2\n    UNUSED [-1,1] : 0.0000\n 2 parameters total, 1 used.\n'


class ParameterSnapshotTests(unittest.TestCase):
    def test_retained_development_result_reproduces(self):
        packet = Path(__file__).resolve().parents[1] / 'evidence/task-parameters-2026-09-30'
        result = runpy.run_path(str(packet / 'summarize.py'))['summarize']()
        self.assertEqual(result, json.loads((packet / 'results.json').read_text()))
        self.assertTrue(result['validity']['valid'])
        for phase, snapshot in result['snapshots'].items():
            self.assertTrue(snapshot['complete'])
            self.assertEqual(snapshot['captured_count'], snapshot['expected_count'])
            self.assertGreater(snapshot['captured_count'], snapshot['used_count'])
            self.assertEqual(result['override_mismatches'][phase], {})
            identity = result['snapshot_identities'][phase]
            path = packet / 'run' / identity['file']
            self.assertEqual(identity['sha256'], hashlib.sha256(path.read_bytes()).hexdigest())

    def test_unused_parameter_is_read_at_full_precision(self):
        vehicle = SimpleNamespace(param_types={'USED': 6, 'UNUSED': 9},
                                  read_param=lambda name: {'USED': 2, 'UNUSED': 0.000012345}[name])
        with tempfile.TemporaryDirectory() as d, patch('harness.run_case.subprocess.run',
                return_value=SimpleNamespace(stdout=INVENTORY, stderr='', returncode=0)):
            snapshot = capture_parameters(vehicle, Path('/build'), Path(d), 'before', lambda _: None)
            self.assertTrue(snapshot['complete'])
            self.assertFalse(snapshot['atomic'])
            self.assertEqual(snapshot['parameters']['UNUSED'], {'type': 9, 'value': 0.000012345})
            self.assertEqual(snapshot['parameters']['USED']['value'], 2)

    def test_missing_inventory_entry_is_refused(self):
        with tempfile.TemporaryDirectory() as d, patch('harness.run_case.subprocess.run',
                return_value=SimpleNamespace(stdout=INVENTORY.replace('2 parameters total', '3 parameters total'),
                                             stderr='', returncode=0)):
            with self.assertRaisesRegex(RuntimeError, 'inventory'):
                capture_parameters(SimpleNamespace(), Path('/build'), Path(d), 'before', lambda _: None)
            self.assertFalse(json.loads((Path(d)/'parameters-before.json').read_text())['complete'])

    def test_missing_reply_keeps_partial_snapshot_and_stops_capture(self):
        def read(name):
            if name == 'UNUSED':
                raise RuntimeError('missing reply')
            return 2
        with tempfile.TemporaryDirectory() as d, patch('harness.run_case.subprocess.run',
                return_value=SimpleNamespace(stdout=INVENTORY, stderr='', returncode=0)):
            vehicle = SimpleNamespace(param_types={'USED': 6}, read_param=read)
            with self.assertRaisesRegex(RuntimeError, 'missing reply'):
                capture_parameters(vehicle, Path('/build'), Path(d), 'before', lambda _: None)
            saved = json.loads((Path(d)/'parameters-before.json').read_text())
            self.assertFalse(saved['complete'])
            self.assertEqual(set(saved['parameters']), {'USED'})


if __name__ == '__main__':
    unittest.main()

"""Full registry capture includes unused parameters and preserves typed transport."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from harness import cases, run_case


class SnapshotTests(unittest.TestCase):
    def test_typed_unused_registry_entry_is_captured_and_missing_reply_is_incomplete(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'src/lib/parameters').mkdir(parents=True)
            (root / 'parameters.xml').write_text(
                '<parameters><parameter name="ACTION" type="INT32"/>'
                '<parameter name="UNUSED" type="FLOAT"/></parameters>')
            (root / 'src/lib/parameters/px4_parameters.hpp').write_text(
                'enum class params : uint16_t {\nACTION,\nUNUSED,\n};')
            vehicle = run_case.Vehicle(None, lambda _: None)
            values = {'ACTION': (6, struct.unpack('<f', struct.pack('<i', 2))[0]),
                      'UNUSED': (9, 0.25)}
            def read(name):
                typ, val = values[name]
                return vehicle.decode_param(SimpleNamespace(param_id=name, param_type=typ, param_value=val))
            with patch.object(run_case, 'mav', SimpleNamespace(MAV_PARAM_TYPE_INT32=6, MAV_PARAM_TYPE_REAL32=9)), \
                 patch.object(vehicle, 'read_param', side_effect=read):
                vehicle.snapshot_parameters(root, root)
                snapshot = json.loads((root / 'parameters-full.json').read_text())
                self.assertTrue(snapshot['complete'])
                self.assertEqual(set(snapshot['parameters']), {'ACTION', 'UNUSED'})
                self.assertEqual(snapshot['parameters']['ACTION'],
                                 dict(type='INT32', value=2, wire_hex='02000000'))
                del values['UNUSED']
                with self.assertRaises(KeyError):
                    vehicle.snapshot_parameters(root, root)
                partial = json.loads((root / 'parameters-full.json').read_text())
                self.assertFalse(partial['complete'])
                self.assertEqual(set(partial['parameters']), {'ACTION'})

    def test_development_schedule_does_not_accept_frozen_seed(self):
        config = 'px4-v1.17.0-sih-quadx-rtl'
        for seed in cases.SEED_OFFSET_S:
            with self.assertRaises(ValueError):
                cases.resolve(config, 'datalink_loss', seed, development_offset_s=0)
        case = cases.resolve(config, 'datalink_loss', 101, development_offset_s=0.4)
        self.assertIn('development101', case['case_id'])
        self.assertEqual(case['inject_at_vehicle_s'], cases.NOMINAL_INJECT_T_S + 0.4)

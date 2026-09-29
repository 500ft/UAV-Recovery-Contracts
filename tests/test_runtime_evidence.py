"""The executed diagnosis remains reproducible from its retained raw records."""
import json
from pathlib import Path
import runpy
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKET = ROOT / 'evidence/task-runtime-2026-09-29'


class RuntimeEvidenceTests(unittest.TestCase):
    def test_retained_runs_reproduce_the_diagnosis(self):
        actual = runpy.run_path(str(PACKET / 'analyze.py'))['generate']()
        self.assertEqual(actual, json.loads((PACKET / 'results.json').read_text()))
        runs = actual['runs']
        bad, fixed = runs['instrumented'], runs['corrected-instrumented']
        self.assertNotEqual(bad['effective_nav_dll_act'],
                            [bad['reported_override_readback']['NAV_DLL_ACT']])
        self.assertEqual(fixed['effective_nav_dll_act'],
                         [fixed['reported_override_readback']['NAV_DLL_ACT']])
        self.assertGreater(fixed['complete_native_tuples'], 0)
        self.assertEqual(fixed['incomplete_native_tuples'], 0)
        self.assertGreater(fixed['selected_rtl_after_consumed_flag_s'], 0)
        self.assertEqual(runs['baseline-authorized']['binary_sha256'],
                         runs['corrected-original-binary']['binary_sha256'])
        self.assertFalse(runs['baseline-authorized']['post_injection_native_mode_events'])
        for name in ('corrected-instrumented', 'corrected-original-binary'):
            self.assertTrue(runs[name]['valid']['valid'])
            self.assertIn('AUTO_RTL', [e['to'] for e in runs[name]['post_injection_native_mode_events']])


if __name__ == '__main__':
    unittest.main()

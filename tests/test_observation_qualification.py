"""A telemetry timeout anchor must never substitute for a heartbeat receive."""
from pathlib import Path
import runpy
import unittest


class ObservationQualificationTests(unittest.TestCase):
    def test_receive_anchor_and_quantized_execution_are_distinct(self):
        module = runpy.run_path(str(Path(__file__).resolve().parents[1] /
                                   'evidence/task-observation-qualification-2026-10-04/analyze.py'))
        records = module['time_records']('''UAV_TIME rx t=100 ch=0 sys=255 comp=190
UAV_TIME telem t=120 ch=0 gcs=1
UAV_TIME age t=130 ch=0 last=100 gcs=0
UAV_TIME telem t=134 ch=0 gcs=0
UAV_TIME detector t=220 end=224 anchor=120 lost=1
UAV_TIME selected t=230 update=228 action=5
UAV_TIME selected t=280 update=280 action=6
UAV_TIME navigator t=280 end=280 nav=5 mode=5 sp=1
''')
        result = module['native_timing'](records, 150)
        self.assertEqual(result['receive_to_detector_interval_us'], [120, 124])
        self.assertEqual(result['receive_to_selected_rtl_us'], 180)
        self.assertEqual(result['publications_matching_detector_anchor'][0]['t'], 120)
        self.assertEqual(result['first_false_telemetry_publication']['t'], 134)
        self.assertEqual(result['first_navigator_rtl_execution_bracket']['end'], 280)
        self.assertIn('do not prove zero', result['clock_limit'])
        records.pop('rx')
        missing = module['native_timing'](records, 150)
        self.assertIsNone(missing['last_observed_qualifying_receive'])
        self.assertIsNone(missing['receive_to_detector_interval_us'])
        self.assertIsNone(missing['receive_to_selected_rtl_us'])


if __name__ == '__main__':
    unittest.main()

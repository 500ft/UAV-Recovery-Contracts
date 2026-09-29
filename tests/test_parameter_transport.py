"""PX4 copies PARAM_SET's float bytes into typed storage; replies use the same encoding.

The fake receiver follows mavlink_parameters.cpp at the pinned firmware. It
would store float(2)'s bits as an integer under the former runner.
"""
import struct
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from harness import run_case


INT32, REAL32 = 6, 9


class Receiver:
    def __init__(self, value=0, ptype=INT32):
        self.value, self.ptype = value, ptype
        self.mav = self
        self.queue = []

    def reply(self):
        wire = (struct.unpack('<f', struct.pack('<i', self.value))[0]
                if self.ptype == INT32 else self.value)
        self.queue.append(SimpleNamespace(param_id='TEST', param_value=wire, param_type=self.ptype))

    def param_request_read_send(self, *args):
        self.reply()

    def param_set_send(self, system, component, name, wire, ptype):
        if ptype != self.ptype:
            raise AssertionError('PX4 rejects a parameter type mismatch')
        self.value = (struct.unpack('<i', struct.pack('<f', wire))[0]
                      if ptype == INT32 else wire)
        self.reply()

    def recv_match(self, **kwargs):
        return self.queue.pop(0) if self.queue else None


class ParameterTransportTests(unittest.TestCase):
    def setUp(self):
        mock = patch.object(run_case, 'mav', SimpleNamespace(MAV_PARAM_TYPE_INT32=INT32,
                                                           MAV_PARAM_TYPE_REAL32=REAL32))
        mock.start()
        self.addCleanup(mock.stop)

    def test_integer_writes_reach_integer_storage(self):
        for value in (0, 1, 2, 3, -1, 65536):
            with self.subTest(value=value):
                receiver = Receiver()
                vehicle = run_case.Vehicle(receiver, lambda _: None)
                vehicle.set_param('TEST', value)
                self.assertEqual(receiver.value, value)
                self.assertEqual(vehicle.read_param('TEST'), value)

    def test_corrupted_numeric_float_reply_is_not_falsely_accepted(self):
        receiver = Receiver(value=1073741824)
        vehicle = run_case.Vehicle(receiver, lambda _: None)
        self.assertEqual(vehicle.read_param('TEST'), receiver.value)
        self.assertNotEqual(vehicle.read_param('TEST'), 2)

    def test_parameter_type_comes_from_vehicle_not_python_literal(self):
        for ptype, requested in ((REAL32, 5), (INT32, 2.0)):
            with self.subTest(ptype=ptype):
                receiver = Receiver(ptype=ptype)
                vehicle = run_case.Vehicle(receiver, lambda _: None)
                vehicle.set_param('TEST', requested)
                self.assertEqual(receiver.value, requested)

    def test_tiny_real_float_is_not_reinterpreted_as_integer(self):
        receiver = Receiver(value=1e-35, ptype=REAL32)
        vehicle = run_case.Vehicle(receiver, lambda _: None)
        self.assertEqual(vehicle.read_param('TEST'), 1e-35)


if __name__ == '__main__':
    unittest.main()

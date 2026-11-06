import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml.registry import default_registry
from duml.codecs import encode_payload, decode_payload, CodecError


class TestCodecs(unittest.TestCase):
    def setUp(self):
        self.reg = default_registry()

    def test_gimbal_control_roundtrip(self):
        spec = self.reg.get(0x04, 0x01)
        vals = {'gimbal_control_unkn0': 1024, 'gimbal_control_unkn1': 500, 'gimbal_control_unkn2': 900}
        payload = encode_payload(spec.fields, vals)
        self.assertEqual(len(payload), 6)
        decoded = decode_payload(spec.fields, payload)
        for k, v in vals.items():
            self.assertEqual(decoded[k], v)

    def test_gimbal_control_with_optional_padding_branch(self):
        spec = self.reg.get(0x04, 0x01)
        vals = {'gimbal_control_unkn0': 1, 'gimbal_control_unkn1': 2, 'gimbal_control_unkn2': 3,
                'gimbal_control_padding': b'\x00\x00'}
        payload = encode_payload(spec.fields, vals, total_len=8)
        self.assertEqual(len(payload), 8)
        decoded = decode_payload(spec.fields, payload)
        self.assertEqual(decoded['gimbal_control_unkn0'], 1)
        self.assertIn('gimbal_control_padding', decoded)

    def test_rc_push_param_bitfields_roundtrip(self):
        spec = self.reg.get(0x06, 0x05)
        vals = {
            'rc_push_param_aileron': 1500, 'rc_push_param_elevator': 1500,
            'rc_push_param_throttle': 1000, 'rc_push_param_rudder': 1500,
            'rc_push_param_gyro_value': 0,
            'rc_push_param_wheel_click_status': 1, 'rc_push_param_wheel_offset': 0x1F,
            'rc_push_param_not_wheel_positive': 1, 'rc_push_param_wheel_changed': 1,
            'rc_push_param_go_home_button_pressed': 1, 'rc_push_param_mode': 3,
            'rc_push_param_get_foot_stool': 2,
        }
        payload = encode_payload(spec.fields, vals)
        decoded = decode_payload(spec.fields, payload)
        for k, v in vals.items():
            self.assertEqual(decoded[k], v, f"{k} roundtrip mismatch")

    def test_bitfield_merge_does_not_clobber_siblings(self):
        # setting wheel_offset should not disturb wheel_click_status in the
        # same byte, and vice versa
        spec = self.reg.get(0x06, 0x05)
        base = {'rc_push_param_aileron': 0, 'rc_push_param_elevator': 0,
                'rc_push_param_throttle': 0, 'rc_push_param_rudder': 0,
                'rc_push_param_gyro_value': 0}
        v1 = dict(base, rc_push_param_wheel_click_status=1, rc_push_param_wheel_offset=0)
        v2 = dict(base, rc_push_param_wheel_click_status=0, rc_push_param_wheel_offset=0x1F)
        p1 = encode_payload(spec.fields, v1)
        p2 = encode_payload(spec.fields, v2)
        d1 = decode_payload(spec.fields, p1)
        d2 = decode_payload(spec.fields, p2)
        self.assertEqual(d1['rc_push_param_wheel_click_status'], 1)
        self.assertEqual(d1['rc_push_param_wheel_offset'], 0)
        self.assertEqual(d2['rc_push_param_wheel_click_status'], 0)
        self.assertEqual(d2['rc_push_param_wheel_offset'], 0x1F)

    def test_unknown_command_raw_passthrough(self):
        raw = b'\xDE\xAD\xBE\xEF'
        payload = encode_payload(None, {'raw': raw})
        self.assertEqual(payload, raw)
        decoded = decode_payload(None, raw)
        self.assertEqual(decoded, {'raw': raw})

    def test_unregistered_variant_raises(self):
        spec = self.reg.get(0x04, 0x01)
        with self.assertRaises(CodecError):
            encode_payload(spec.fields, {}, variant='totally_nonexistent_branch_xyz')

    def test_battery_push_common_info_roundtrip(self):
        spec = self.reg.get(0x0d, 0x06)
        vals = {
            'design_capacity': 6000, 'full_charge_capacity': 5800,
            'remaining_capacity': 3000, 'pack_voltage': 15400,
            'current': -2500, 'life_percentage': 96, 'capacity_percentage': 51,
            'temperature': 253, 'cycle_count': 42, 'serial_number': 0x1234,
            'cell1': 3850, 'cell2': 3851, 'cell3': 3849, 'cell4': 3850,
            'cell5': 3848, 'cell6': 3852, 'average_current': -2400,
            'unknown20': 0, 'error_count': 0, 'n_discharge_times': 42,
            'current_status': 0,
        }
        payload = encode_payload(spec.fields, vals)
        self.assertEqual(len(payload), 45)
        decoded = decode_payload(spec.fields, payload)
        for k, v in vals.items():
            self.assertEqual(decoded[k], v, f"{k} mismatch")


if __name__ == '__main__':
    unittest.main()

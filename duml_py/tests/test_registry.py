import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml.registry import CommandRegistry, default_registry


class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.reg = default_registry()

    def test_loads_nonzero_commands(self):
        stats = self.reg.stats()
        self.assertGreater(stats['total'], 800)
        self.assertGreater(stats['full'], 100)

    def test_known_command_lookup(self):
        spec = self.reg.get(0x00, 0x00)
        self.assertIsNotNone(spec)
        self.assertEqual(spec.name, 'Ping')
        self.assertEqual(spec.cmd_set_name, 'General')

    def test_unregistered_pair_still_returns_stub(self):
        spec = self.reg.require(0x1F, 0xFE)
        self.assertEqual(spec.decode_status, 'none')
        self.assertIsNone(spec.fields)

    def test_find_by_name(self):
        hits = self.reg.find_by_name('gimbal control')
        self.assertTrue(any(h.cmd_id == 0x01 and h.cmd_set == 0x04 for h in hits))

    def test_by_cmd_set_sorted(self):
        specs = self.reg.by_cmd_set(0x04)
        ids = [s.cmd_id for s in specs]
        self.assertEqual(ids, sorted(ids))

    def test_battery_push_common_info_present(self):
        # one of two genuinely new decodes added this round, cross-referenced
        # from the P3 flight-recorder dissector
        spec = self.reg.get(0x0d, 0x06)
        self.assertEqual(spec.decode_status, 'full')
        self.assertEqual(spec.source, 'flyrec_crossref')
        names = {f['name'] for f in spec.fields}
        self.assertIn('cell1', names)
        self.assertIn('pack_voltage', names)

    def test_flyc_battery_status_present(self):
        # the other genuinely new decode, cross-referenced from the Mavic
        # flight-recorder dissector; also added to dji-dumlv1-flyc.lua
        spec = self.reg.get(0x03, 0x0a)
        self.assertEqual(spec.decode_status, 'full')
        self.assertEqual(spec.source, 'flyrec_crossref')
        names = {f['name'] for f in spec.fields}
        self.assertIn('volverylow', names)
        self.assertIn('all', names)


if __name__ == '__main__':
    unittest.main()

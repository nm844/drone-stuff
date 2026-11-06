import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml.frame import Frame, FrameError, crc8, crc16, CRC8_TABLE, CRC16_TABLE, iter_frames
from duml.enums import DeviceType, AckType, PacketType


class TestCrc(unittest.TestCase):
    def test_crc8_table_matches_firmware(self):
        # First 16 bytes of DjiCrc8Table, confirmed byte-for-byte against
        # disasm/binding/deps/libduml_frwk.so (file offset 0xfe800).
        self.assertEqual(
            CRC8_TABLE[:16],
            bytes([0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83,
                   0xC2, 0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41]))

    def test_crc16_table_matches_firmware(self):
        self.assertEqual(
            CRC16_TABLE[:8],
            [0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF])

    def test_crc8_empty(self):
        self.assertEqual(crc8(b''), 0x77)  # unchanged seed over zero bytes

    def test_crc16_zero_length_is_0xffff(self):
        # Matches the firmware's explicit `if (len==0) return 0xFFFF;` edge case
        self.assertEqual(crc16(b''), 0xFFFF)

    def test_header_crc8_known_vector(self):
        # bytes [0x55, 0x0D, 0x04] -> header CRC8 as produced by a real encode()
        f = Frame(sender_type=0, receiver_type=0, cmd_set=0, cmd_id=0, payload=b'')
        enc = f.encode()
        self.assertEqual(enc[0], 0x55)
        self.assertEqual(crc8(enc[0:3]), enc[3])


class TestFrameRoundTrip(unittest.TestCase):
    def test_empty_payload_roundtrip(self):
        f = Frame(sender_type=int(DeviceType.PC), receiver_type=int(DeviceType.FLIGHT_CONTROLLER),
                  cmd_set=0x00, cmd_id=0x00, seq_num=0x1234)
        enc = f.encode()
        dec = Frame.decode(enc)
        self.assertEqual(dec.sender_type, f.sender_type)
        self.assertEqual(dec.receiver_type, f.receiver_type)
        self.assertEqual(dec.cmd_set, f.cmd_set)
        self.assertEqual(dec.cmd_id, f.cmd_id)
        self.assertEqual(dec.seq_num, f.seq_num)
        self.assertEqual(dec.payload, b'')

    def test_payload_roundtrip(self):
        payload = bytes(range(32))
        f = Frame(sender_type=int(DeviceType.APP), receiver_type=int(DeviceType.GIMBAL),
                  cmd_set=0x04, cmd_id=0x01, payload=payload, seq_num=42,
                  ack_type=int(AckType.ACK_AFTER_EXEC), packet_type=int(PacketType.RESPONSE))
        enc = f.encode()
        dec = Frame.decode(enc)
        self.assertEqual(dec.payload, payload)
        self.assertEqual(dec.ack_type, int(AckType.ACK_AFTER_EXEC))
        self.assertEqual(dec.packet_type, int(PacketType.RESPONSE))

    def test_sender_receiver_index_bits(self):
        f = Frame(sender_type=5, sender_index=3, receiver_type=7, receiver_index=2,
                  cmd_set=1, cmd_id=1)
        dec = Frame.decode(f.encode())
        self.assertEqual(dec.sender_type, 5)
        self.assertEqual(dec.sender_index, 3)
        self.assertEqual(dec.receiver_type, 7)
        self.assertEqual(dec.receiver_index, 2)

    def test_corrupted_header_crc_rejected(self):
        f = Frame(sender_type=1, receiver_type=1, cmd_set=1, cmd_id=1)
        enc = bytearray(f.encode())
        enc[3] ^= 0xFF  # corrupt header CRC8 byte
        with self.assertRaises(FrameError):
            Frame.decode(bytes(enc))

    def test_corrupted_body_crc_rejected(self):
        f = Frame(sender_type=1, receiver_type=1, cmd_set=4, cmd_id=1, payload=b'\x01\x02\x03\x04')
        enc = bytearray(f.encode())
        enc[12] ^= 0xFF  # corrupt a payload byte -> CRC16 mismatch
        with self.assertRaises(FrameError):
            Frame.decode(bytes(enc))

    def test_bad_sof_rejected(self):
        f = Frame(sender_type=1, receiver_type=1, cmd_set=1, cmd_id=1)
        enc = bytearray(f.encode())
        enc[0] = 0x00
        with self.assertRaises(FrameError):
            Frame.decode(bytes(enc))

    def test_too_short_buffer_rejected(self):
        with self.assertRaises(FrameError):
            Frame.decode(b'\x55\x00')

    def test_iter_frames_back_to_back(self):
        f1 = Frame(sender_type=1, receiver_type=1, cmd_set=0, cmd_id=0, seq_num=1)
        f2 = Frame(sender_type=2, receiver_type=2, cmd_set=0, cmd_id=1, seq_num=2, payload=b'\xAA\xBB')
        buf = f1.encode() + f2.encode()
        frames = list(iter_frames(buf))
        self.assertEqual(len(frames), 2)
        self.assertEqual(frames[0].seq_num, 1)
        self.assertEqual(frames[1].seq_num, 2)
        self.assertEqual(frames[1].payload, b'\xAA\xBB')

    def test_encrypted_payload_rejected_by_encoder(self):
        from duml.enums import EncryptType
        f = Frame(sender_type=1, receiver_type=1, cmd_set=0, cmd_id=0,
                  encrypt_type=int(EncryptType.AES_128))
        with self.assertRaises(FrameError):
            f.encode()


if __name__ == '__main__':
    unittest.main()

"""
DUML v1 wire-frame codec: encode/decode the 11-byte header + payload + CRC16
trailer. CRC8/CRC16 tables and algorithm, and every header bit layout below,
are confirmed by disassembling this project's own WM260 firmware
(libduml_frwk.so -- CalCrc8/CalCrc16/DJI_Frame_Cap). See
../../DUML_PROTOCOL/00_FRAME_FORMAT.md for the full writeup.

Frame layout::

    0       SOF, always 0x55
    1-2     length(10 bits) | version(6 bits), uint16 LE
    3       header_crc8 = CRC8(seed=0x77, bytes[0:3])
    4       sender_info: type(bits0-4) | index(bits5-7)
    5       receiver_info: type(bits0-4) | index(bits5-7)
    6-7     seq_num, uint16 LE
    8       cmd_type_data: encrypt_type(bits0-2) | ack_type(bits5-6) | packet_type(bit7)
    9       cmd_set
    10      cmd_id
    11..N-3 payload (length = whole_length - 13)
    N-2..N-1 crc16 = CRC16(seed=0x3692, bytes[0:N-2])
"""
from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Optional

from .enums import AckType, EncryptType, PacketType

SOF = 0x55
HEADER_LEN = 11      # bytes 0..10 inclusive
CRC16_LEN = 2
MIN_FRAME_LEN = HEADER_LEN + CRC16_LEN  # 13, matches firmware's "offset <= 12 -> reject"

# --- CRC8 table (confirmed byte-identical to this firmware's DjiCrc8Table) ---
CRC8_TABLE = bytes([
    0x00, 0x5E, 0xBC, 0xE2, 0x61, 0x3F, 0xDD, 0x83, 0xC2, 0x9C, 0x7E, 0x20, 0xA3, 0xFD, 0x1F, 0x41,
    0x9D, 0xC3, 0x21, 0x7F, 0xFC, 0xA2, 0x40, 0x1E, 0x5F, 0x01, 0xE3, 0xBD, 0x3E, 0x60, 0x82, 0xDC,
    0x23, 0x7D, 0x9F, 0xC1, 0x42, 0x1C, 0xFE, 0xA0, 0xE1, 0xBF, 0x5D, 0x03, 0x80, 0xDE, 0x3C, 0x62,
    0xBE, 0xE0, 0x02, 0x5C, 0xDF, 0x81, 0x63, 0x3D, 0x7C, 0x22, 0xC0, 0x9E, 0x1D, 0x43, 0xA1, 0xFF,
    0x46, 0x18, 0xFA, 0xA4, 0x27, 0x79, 0x9B, 0xC5, 0x84, 0xDA, 0x38, 0x66, 0xE5, 0xBB, 0x59, 0x07,
    0xDB, 0x85, 0x67, 0x39, 0xBA, 0xE4, 0x06, 0x58, 0x19, 0x47, 0xA5, 0xFB, 0x78, 0x26, 0xC4, 0x9A,
    0x65, 0x3B, 0xD9, 0x87, 0x04, 0x5A, 0xB8, 0xE6, 0xA7, 0xF9, 0x1B, 0x45, 0xC6, 0x98, 0x7A, 0x24,
    0xF8, 0xA6, 0x44, 0x1A, 0x99, 0xC7, 0x25, 0x7B, 0x3A, 0x64, 0x86, 0xD8, 0x5B, 0x05, 0xE7, 0xB9,
    0x8C, 0xD2, 0x30, 0x6E, 0xED, 0xB3, 0x51, 0x0F, 0x4E, 0x10, 0xF2, 0xAC, 0x2F, 0x71, 0x93, 0xCD,
    0x11, 0x4F, 0xAD, 0xF3, 0x70, 0x2E, 0xCC, 0x92, 0xD3, 0x8D, 0x6F, 0x31, 0xB2, 0xEC, 0x0E, 0x50,
    0xAF, 0xF1, 0x13, 0x4D, 0xCE, 0x90, 0x72, 0x2C, 0x6D, 0x33, 0xD1, 0x8F, 0x0C, 0x52, 0xB0, 0xEE,
    0x32, 0x6C, 0x8E, 0xD0, 0x53, 0x0D, 0xEF, 0xB1, 0xF0, 0xAE, 0x4C, 0x12, 0x91, 0xCF, 0x2D, 0x73,
    0xCA, 0x94, 0x76, 0x28, 0xAB, 0xF5, 0x17, 0x49, 0x08, 0x56, 0xB4, 0xEA, 0x69, 0x37, 0xD5, 0x8B,
    0x57, 0x09, 0xEB, 0xB5, 0x36, 0x68, 0x8A, 0xD4, 0x95, 0xCB, 0x29, 0x77, 0xF4, 0xAA, 0x48, 0x16,
    0xE9, 0xB7, 0x55, 0x0B, 0x88, 0xD6, 0x34, 0x6A, 0x2B, 0x75, 0x97, 0xC9, 0x4A, 0x14, 0xF6, 0xA8,
    0x74, 0x2A, 0xC8, 0x96, 0x15, 0x4B, 0xA9, 0xF7, 0xB6, 0xE8, 0x0A, 0x54, 0xD7, 0x89, 0x6B, 0x35,
])

# --- CRC16 table (confirmed byte-identical, standard reflected CRC-16/CCITT) ---
CRC16_TABLE = [
    0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF, 0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
    0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E, 0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
    0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD, 0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
    0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C, 0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
    0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB, 0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
    0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A, 0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
    0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9, 0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
    0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738, 0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
    0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7, 0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
    0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036, 0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
    0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5, 0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
    0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134, 0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
    0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3, 0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
    0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232, 0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
    0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1, 0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
    0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330, 0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78,
]

CRC8_SEED = 0x77
CRC16_SEED = 0x3692


def crc8(data: bytes, seed: int = CRC8_SEED) -> int:
    """CalCrc8(seed, data) -- confirmed from firmware disassembly."""
    v = seed
    for b in data:
        v = CRC8_TABLE[v ^ b]
    return v


def crc16(data: bytes, seed: int = CRC16_SEED) -> int:
    """CalCrc16(seed, data) -- confirmed from firmware disassembly."""
    if len(data) == 0:
        return 0xFFFF
    v = seed
    for b in data:
        idx = (b ^ v) & 0xFF
        v = CRC16_TABLE[idx] ^ (v >> 8)
    return v


class FrameError(ValueError):
    """Raised for any malformed/invalid DUML frame."""


@dataclass
class Frame:
    """A fully parsed (or about-to-be-encoded) DUML v1 frame."""
    sender_type: int
    receiver_type: int
    cmd_set: int
    cmd_id: int
    payload: bytes = b""
    sender_index: int = 0
    receiver_index: int = 0
    seq_num: int = 0
    packet_type: int = int(PacketType.REQUEST)
    ack_type: int = int(AckType.NO_ACK_NEEDED)
    encrypt_type: int = int(EncryptType.NONE)
    version: int = 1
    # populated on decode only, informational:
    raw: Optional[bytes] = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    def encode(self) -> bytes:
        if self.encrypt_type != int(EncryptType.NONE):
            raise FrameError(
                "encrypt_type != NONE is not supported by this encoder: the "
                "wire format gives no public algorithm/key material for AES/"
                "DES/self-defined -- only XOR(3) is even partially documented "
                "upstream and still needs a per-link key. Construct an "
                "already-encrypted payload yourself and pass it in with "
                "encrypt_type set, or leave encrypt_type=NONE."
            )
        if len(self.payload) > 0x3FF - HEADER_LEN - CRC16_LEN:
            raise FrameError(f"payload too long ({len(self.payload)} bytes) for 10-bit length field")

        whole_length = HEADER_LEN + len(self.payload) + CRC16_LEN
        ver_length_tag = (whole_length & 0x03FF) | ((self.version & 0x3F) << 10)

        header = bytearray()
        header.append(SOF)
        header += struct.pack('<H', ver_length_tag)
        header.append(0)  # placeholder for header_crc8, filled below
        hcrc = crc8(bytes(header[0:3]))
        header[3] = hcrc

        sender_info = (self.sender_type & 0x1F) | ((self.sender_index & 0x07) << 5)
        receiver_info = (self.receiver_type & 0x1F) | ((self.receiver_index & 0x07) << 5)
        header.append(sender_info)
        header.append(receiver_info)
        header += struct.pack('<H', self.seq_num & 0xFFFF)

        cmd_type_data = ((self.encrypt_type & 0x07)
                         | ((self.ack_type & 0x03) << 5)
                         | ((self.packet_type & 0x01) << 7))
        header.append(cmd_type_data)
        header.append(self.cmd_set & 0xFF)
        header.append(self.cmd_id & 0xFF)

        assert len(header) == HEADER_LEN, len(header)

        body = bytes(header) + self.payload
        fcrc = crc16(body)
        return body + struct.pack('<H', fcrc)

    # ------------------------------------------------------------------
    @classmethod
    def decode(cls, buf: bytes, *, verify_crc: bool = True) -> "Frame":
        """Decode exactly one frame from the start of `buf`. Raises
        FrameError if malformed. Does not consume/return leftover bytes --
        use `iter_frames`/StreamFramer for a continuous byte stream."""
        if len(buf) < MIN_FRAME_LEN:
            raise FrameError(f"buffer too short ({len(buf)} bytes, need >= {MIN_FRAME_LEN})")
        if buf[0] != SOF:
            raise FrameError(f"bad SOF byte 0x{buf[0]:02X}, expected 0x55")

        ver_length_tag = struct.unpack_from('<H', buf, 1)[0]
        whole_length = ver_length_tag & 0x03FF
        version = (ver_length_tag >> 10) & 0x3F

        if whole_length <= 12:
            raise FrameError(f"frame length {whole_length} too short (firmware rejects <=12)")
        if len(buf) < whole_length:
            raise FrameError(f"buffer has {len(buf)} bytes, frame declares {whole_length}")

        if verify_crc:
            hcrc = crc8(buf[0:3])
            if hcrc != buf[3]:
                raise FrameError(f"header CRC8 mismatch: got 0x{buf[3]:02X}, expected 0x{hcrc:02X}")

        if version != 1:
            raise FrameError(f"unsupported protocol version {version} (only v1 is implemented)")

        sender_info = buf[4]
        receiver_info = buf[5]
        seq_num = struct.unpack_from('<H', buf, 6)[0]
        cmd_type_data = buf[8]
        cmd_set = buf[9]
        cmd_id = buf[10]
        payload = bytes(buf[11:whole_length - 2])

        if verify_crc:
            fcrc = crc16(buf[0:whole_length - 2])
            got_fcrc = struct.unpack_from('<H', buf, whole_length - 2)[0]
            if fcrc != got_fcrc:
                raise FrameError(f"frame CRC16 mismatch: got 0x{got_fcrc:04X}, expected 0x{fcrc:04X}")

        return cls(
            sender_type=sender_info & 0x1F,
            sender_index=(sender_info >> 5) & 0x07,
            receiver_type=receiver_info & 0x1F,
            receiver_index=(receiver_info >> 5) & 0x07,
            seq_num=seq_num,
            packet_type=(cmd_type_data >> 7) & 0x01,
            ack_type=(cmd_type_data >> 5) & 0x03,
            encrypt_type=cmd_type_data & 0x07,
            cmd_set=cmd_set,
            cmd_id=cmd_id,
            payload=payload,
            version=version,
            raw=bytes(buf[0:whole_length]),
        )

    @property
    def whole_length(self) -> int:
        return HEADER_LEN + len(self.payload) + CRC16_LEN


def iter_frames(buf: bytes, *, verify_crc: bool = True):
    """Yield every valid Frame found back-to-back starting at buf[0].
    Stops at the first byte that isn't a valid frame start (does not
    resynchronize mid-buffer -- use StreamFramer for noisy/live streams)."""
    offset = 0
    while offset < len(buf):
        try:
            fr = Frame.decode(buf[offset:], verify_crc=verify_crc)
        except FrameError:
            break
        yield fr
        offset += fr.whole_length

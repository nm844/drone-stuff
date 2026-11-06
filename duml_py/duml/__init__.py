"""
duml -- a DUML v1 (DJI Universal Markup Language) protocol implementation:
frame codec, command registry, payload field codecs, and transports for
sending/receiving any supported command.

See ../README.md for an overview and ../../DUML_PROTOCOL/ for the full
protocol reference this package is generated from / verified against.
"""
from .frame import Frame, FrameError, crc8, crc16, iter_frames
from .enums import (
    DeviceType, AckType, EncryptType, PacketType, CmdSet,
    CMD_SET_NAMES, DEVICE_TYPE_NAMES, CMD_SET_TYPICAL_RECEIVER,
)
from .registry import CommandRegistry, CommandSpec, default_registry
from .codecs import decode_payload, encode_payload, CodecError
from .client import DumlClient, DecodedFrame

__all__ = [
    "Frame", "FrameError", "crc8", "crc16", "iter_frames",
    "DeviceType", "AckType", "EncryptType", "PacketType", "CmdSet",
    "CMD_SET_NAMES", "DEVICE_TYPE_NAMES", "CMD_SET_TYPICAL_RECEIVER",
    "CommandRegistry", "CommandSpec", "default_registry",
    "decode_payload", "encode_payload", "CodecError",
    "DumlClient", "DecodedFrame",
]

__version__ = "0.1.0"

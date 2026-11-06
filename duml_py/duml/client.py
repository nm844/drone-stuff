"""
High-level client: build & send a Frame for any (cmd_set, cmd_id) the
registry knows about (or any raw pair it doesn't -- you just supply raw
payload bytes instead of named fields), and decode incoming frames with
named fields wherever the registry has a known layout.
"""
from __future__ import annotations

import itertools
import threading
import time
from typing import Any, Dict, List, Optional, Tuple

from .codecs import decode_payload, encode_payload
from .enums import AckType, EncryptType, PacketType, DeviceType
from .frame import Frame
from .registry import CommandRegistry, CommandSpec, default_registry
from .transport.base import Transport, StreamFramer, FrameListener


class DecodedFrame:
    """A Frame plus its registry metadata and decoded field dict."""

    def __init__(self, frame: Frame, spec: CommandSpec, fields: Dict[str, Any]):
        self.frame = frame
        self.spec = spec
        self.fields = fields

    def __repr__(self) -> str:
        direction = 'RESPONSE' if self.frame.packet_type else 'REQUEST'
        return (f"<DecodedFrame {DeviceType(self.frame.sender_type).name}"
                f"->{DeviceType(self.frame.receiver_type).name} "
                f"{self.spec.cmd_set_name}/0x{self.spec.cmd_id:02X} "
                f"'{self.spec.name}' {direction} seq={self.frame.seq_num} "
                f"fields={self.fields}>")


class DumlClient:
    """
    Usage::

        client = DumlClient(transport, sender_type=DeviceType.PC)
        client.send_command(CmdSet.GENERAL, 0x00)          # Ping, raw/no fields
        client.send_command(CmdSet.GIMBAL, 0x01,           # Gimbal Control
                             receiver_type=DeviceType.GIMBAL,
                             fields={'gimbal_control_unkn0': 1024,
                                     'gimbal_control_unkn1': 1024,
                                     'gimbal_control_unkn2': 1024})
        for df in client.listen(duration=5):
            print(df)
    """

    def __init__(self, transport: Transport, *,
                 sender_type: int = int(DeviceType.PC), sender_index: int = 0,
                 registry: Optional[CommandRegistry] = None,
                 verify_crc: bool = True):
        self.transport = transport
        self.sender_type = int(sender_type)
        self.sender_index = sender_index
        self.registry = registry or default_registry()
        self.verify_crc = verify_crc
        self._seq = itertools.count(1)
        self._framer = StreamFramer(verify_crc=verify_crc)
        self._pending: Dict[Tuple[int, int, int], List[DecodedFrame]] = {}
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    def next_seq(self) -> int:
        return next(self._seq) & 0xFFFF

    def build_frame(self, cmd_set: int, cmd_id: int, *,
                     receiver_type: int = int(DeviceType.ANY),
                     receiver_index: int = 0,
                     fields: Optional[Dict[str, Any]] = None,
                     raw_payload: Optional[bytes] = None,
                     packet_type: int = int(PacketType.REQUEST),
                     ack_type: int = int(AckType.NO_ACK_NEEDED),
                     variant: Optional[str] = None,
                     seq_num: Optional[int] = None) -> Frame:
        spec = self.registry.require(cmd_set, cmd_id)
        if raw_payload is not None:
            payload = raw_payload
        elif spec.fields:
            payload = encode_payload(spec.fields, fields or {}, packet_type=packet_type, variant=variant)
        else:
            payload = encode_payload(None, {'raw': (fields or {}).get('raw', b'')})
        return Frame(
            sender_type=self.sender_type, sender_index=self.sender_index,
            receiver_type=int(receiver_type), receiver_index=receiver_index,
            cmd_set=cmd_set, cmd_id=cmd_id, payload=payload,
            packet_type=packet_type, ack_type=ack_type,
            seq_num=seq_num if seq_num is not None else self.next_seq(),
        )

    def send_frame(self, frame: Frame) -> Frame:
        self.transport.write(frame.encode())
        return frame

    def send_command(self, cmd_set: int, cmd_id: int, **kwargs) -> Frame:
        """Build and immediately send a command. See build_frame() for kwargs."""
        return self.send_frame(self.build_frame(cmd_set, cmd_id, **kwargs))

    def send_and_wait(self, cmd_set: int, cmd_id: int, *, timeout: float = 2.0,
                       **kwargs) -> Optional["DecodedFrame"]:
        """Send a request (forcing ack_type=ACK_AFTER_EXEC unless overridden)
        and block until a matching Response (same cmd_set/cmd_id/seq_num)
        frame is decoded, or `timeout` elapses."""
        kwargs.setdefault('ack_type', int(AckType.ACK_AFTER_EXEC))
        frame = self.build_frame(cmd_set, cmd_id, **kwargs)
        key = (cmd_set, cmd_id, frame.seq_num)
        with self._lock:
            self._pending[key] = []
        self.send_frame(frame)

        deadline = time.time() + timeout
        while time.time() < deadline:
            self._pump(0.05)
            with self._lock:
                got = self._pending.get(key)
            if got:
                with self._lock:
                    del self._pending[key]
                return got[0]
        with self._lock:
            self._pending.pop(key, None)
        return None

    # ------------------------------------------------------------------
    def decode_incoming(self, raw: bytes) -> DecodedFrame:
        frame = Frame.decode(raw, verify_crc=self.verify_crc)
        return self._wrap(frame)

    def _wrap(self, frame: Frame) -> DecodedFrame:
        spec = self.registry.require(frame.cmd_set, frame.cmd_id)
        fields = decode_payload(spec.fields, frame.payload, packet_type=frame.packet_type)
        return DecodedFrame(frame, spec, fields)

    def _pump(self, timeout: float) -> List[DecodedFrame]:
        data = self.transport.read(max_bytes=4096, timeout=timeout)
        out = []
        if data:
            self._framer.feed(data)
            for fr in self._framer.pop_ready():
                df = self._wrap(fr)
                out.append(df)
                key = (fr.cmd_set, fr.cmd_id, fr.seq_num)
                with self._lock:
                    if key in self._pending:
                        self._pending[key].append(df)
        return out

    def listen(self, duration: Optional[float] = None, poll: float = 0.1):
        """Generator: yields DecodedFrame for every frame received, for
        `duration` seconds (or forever if None)."""
        deadline = None if duration is None else time.time() + duration
        while deadline is None or time.time() < deadline:
            for df in self._pump(poll):
                yield df

    def start_background_listener(self, callback) -> FrameListener:
        """Non-blocking variant: runs in a thread, calls callback(DecodedFrame)."""
        def _cb(frame: Frame) -> None:
            callback(self._wrap(frame))
        listener = FrameListener(self.transport, _cb, verify_crc=self.verify_crc)
        listener.start()
        return listener

"""Transport abstraction + byte-stream framer.

A Transport just needs to move raw bytes in both directions; StreamFramer
does the work of finding valid DUML frames inside a possibly-noisy,
possibly-fragmented byte stream (the same resynchronization approach as the
firmware's own DJI_Frame_Cap: scan for 0x55, validate header CRC8 before
trusting the length field, validate CRC16 before accepting the frame).
"""
from __future__ import annotations

import abc
import threading
import time
from typing import Callable, Iterator, Optional

from ..frame import Frame, FrameError, SOF, HEADER_LEN, crc8


class Transport(abc.ABC):
    """Minimal duplex byte transport."""

    @abc.abstractmethod
    def write(self, data: bytes) -> None:
        ...

    @abc.abstractmethod
    def read(self, max_bytes: int = 4096, timeout: Optional[float] = None) -> bytes:
        """Return whatever bytes are available within `timeout` seconds
        (may return b'' on timeout -- must not block forever)."""
        ...

    def close(self) -> None:
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


class StreamFramer:
    """Feed it bytes as they arrive (`feed`), get back complete, validated
    Frame objects as they become available (`pop_ready` / iterate)."""

    def __init__(self, verify_crc: bool = True):
        self._buf = bytearray()
        self._verify_crc = verify_crc
        self._ready: list[Frame] = []

    def feed(self, data: bytes) -> None:
        self._buf += data
        self._resync_and_parse()

    def _resync_and_parse(self) -> None:
        buf = self._buf
        i = 0
        while True:
            # find next candidate SOF
            idx = buf.find(SOF, i)
            if idx < 0:
                del buf[:len(buf)]  # nothing usable left
                return
            if idx > 0:
                del buf[:idx]
                idx = 0
            if len(buf) < HEADER_LEN:
                return  # wait for more header bytes
            # need length+version to know how much more to wait for
            import struct
            ver_length_tag = struct.unpack_from('<H', buf, 1)[0]
            length = ver_length_tag & 0x03FF
            if length <= 12:
                del buf[0:1]  # bad length, resync past this SOF byte
                i = 0
                continue
            if self._verify_crc and len(buf) >= 4:
                hcrc = crc8(bytes(buf[0:3]))
                if hcrc != buf[3]:
                    del buf[0:1]
                    i = 0
                    continue
            if len(buf) < length:
                return  # wait for the rest of this frame
            try:
                fr = Frame.decode(bytes(buf[0:length]), verify_crc=self._verify_crc)
                self._ready.append(fr)
                del buf[0:length]
                i = 0
                continue
            except FrameError:
                del buf[0:1]
                i = 0
                continue

    def pop_ready(self) -> list[Frame]:
        out = self._ready
        self._ready = []
        return out


class FrameListener:
    """Runs a background thread reading from a Transport, feeding a
    StreamFramer, and calling `callback(frame)` for every decoded frame."""

    def __init__(self, transport: Transport, callback: Callable[[Frame], None],
                 verify_crc: bool = True, poll_timeout: float = 0.2):
        self.transport = transport
        self.callback = callback
        self.framer = StreamFramer(verify_crc=verify_crc)
        self.poll_timeout = poll_timeout
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2)

    def _run(self) -> None:
        while not self._stop.is_set():
            data = self.transport.read(max_bytes=4096, timeout=self.poll_timeout)
            if data:
                self.framer.feed(data)
                for fr in self.framer.pop_ready():
                    try:
                        self.callback(fr)
                    except Exception:
                        pass
            else:
                time.sleep(0.01)

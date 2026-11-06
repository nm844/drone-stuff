"""Serial (UART/USB-CDC) transport, for talking to physical DUML links
(RC, battery/center-board debug UART, gimbal, flight-controller debug port,
etc.) Requires pyserial (`pip install pyserial`)."""
from __future__ import annotations

from typing import Optional

from .base import Transport

try:
    import serial  # type: ignore
except ImportError:  # pragma: no cover
    serial = None


class SerialTransport(Transport):
    def __init__(self, port: str, baudrate: int = 115200, **kwargs):
        if serial is None:
            raise ImportError(
                "pyserial is required for SerialTransport: pip install pyserial"
            )
        self._ser = serial.Serial(port, baudrate=baudrate, timeout=0, **kwargs)

    def write(self, data: bytes) -> None:
        self._ser.write(data)
        self._ser.flush()

    def read(self, max_bytes: int = 4096, timeout: Optional[float] = None) -> bytes:
        """Return available bytes (up to max_bytes). `timeout` is the max
        time to wait for at least one byte if none are already buffered."""
        self._ser.timeout = timeout
        waiting = self._ser.in_waiting
        if waiting:
            return self._ser.read(min(max_bytes, waiting))
        return self._ser.read(1) or b""

    def close(self) -> None:
        self._ser.close()

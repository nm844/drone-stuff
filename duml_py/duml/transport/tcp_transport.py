"""TCP transport, for DUML-over-network bridges (e.g. a USB-bulk<->TCP
proxy, or testing against a recorded/replayed stream served over a socket).
Uses the standard library only."""
from __future__ import annotations

import socket
from typing import Optional

from .base import Transport


class TcpTransport(Transport):
    def __init__(self, host: str, port: int, connect_timeout: float = 5.0):
        self._sock = socket.create_connection((host, port), timeout=connect_timeout)
        self._sock.settimeout(0)

    def write(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read(self, max_bytes: int = 4096, timeout: Optional[float] = None) -> bytes:
        self._sock.settimeout(timeout)
        try:
            return self._sock.recv(max_bytes)
        except (socket.timeout, BlockingIOError):
            return b""

    def close(self) -> None:
        self._sock.close()


class TcpServerTransport(Transport):
    """Listens for a single inbound connection (e.g. acting as the
    ground-side endpoint of a bridge someone else connects to)."""

    def __init__(self, host: str, port: int, accept_timeout: float = 30.0):
        srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((host, port))
        srv.listen(1)
        srv.settimeout(accept_timeout)
        conn, _addr = srv.accept()
        conn.settimeout(0)
        srv.close()
        self._sock = conn

    def write(self, data: bytes) -> None:
        self._sock.sendall(data)

    def read(self, max_bytes: int = 4096, timeout: Optional[float] = None) -> bytes:
        self._sock.settimeout(timeout)
        try:
            return self._sock.recv(max_bytes)
        except (socket.timeout, BlockingIOError):
            return b""

    def close(self) -> None:
        self._sock.close()

"""
Command registry: loads commands.json (generated from the Wireshark
dissector source plus a small number of independently cross-referenced
additions -- see ../../DUML_PROTOCOL/README.md) and gives lookup by
(cmd_set, cmd_id) or by name.

commands.json covers every (cmd_set, cmd_id) pair known from the public
dji-firmware-tools dissector across DJI's whole DUML-speaking product line.
Not every one of these is necessarily reachable on this specific WM260
aircraft/firmware revision -- see DUML_PROTOCOL/01_BINARY_ANALYSIS_FINDINGS.md.
`decode_status` is 'full' only where the payload byte layout is actually
known (156 of 877 at the time this was generated); all others decode to
{'raw': <bytes>} via codecs.decode_payload, which you can still send/receive
and inspect -- you just won't get named fields without further research.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .enums import CMD_SET_NAMES

_DATA_PATH = os.path.join(os.path.dirname(__file__), 'commands.json')


@dataclass
class CommandSpec:
    cmd_set: int
    cmd_id: int
    name: str
    decode_status: str   # 'full' | 'none'
    fields: Optional[List[dict]]
    source: Optional[str] = None
    dissector_fn: Optional[str] = None
    note: Optional[str] = None

    @property
    def cmd_set_name(self) -> str:
        return CMD_SET_NAMES.get(self.cmd_set, f'Unknown(0x{self.cmd_set:02X})')

    def __repr__(self) -> str:
        return (f"<CommandSpec {self.cmd_set_name}/0x{self.cmd_id:02X} "
                f"'{self.name}' decode={self.decode_status}>")


class CommandRegistry:
    def __init__(self, path: str = _DATA_PATH):
        with open(path, 'r') as f:
            raw = json.load(f)
        self._by_key: Dict[Tuple[int, int], CommandSpec] = {}
        self._by_name: Dict[str, List[CommandSpec]] = {}
        for item in raw:
            spec = CommandSpec(
                cmd_set=item['cmd_set'], cmd_id=item['cmd_id'], name=item['name'],
                decode_status=item['decode_status'], fields=item.get('fields'),
                source=item.get('source'), dissector_fn=item.get('dissector_fn'),
                note=item.get('note'),
            )
            self._by_key[(spec.cmd_set, spec.cmd_id)] = spec
            self._by_name.setdefault(spec.name.lower(), []).append(spec)

    def get(self, cmd_set: int, cmd_id: int) -> Optional[CommandSpec]:
        return self._by_key.get((cmd_set, cmd_id))

    def require(self, cmd_set: int, cmd_id: int) -> CommandSpec:
        spec = self.get(cmd_set, cmd_id)
        if spec is None:
            # Unregistered pair: still perfectly sendable/receivable on the
            # wire, we just have no metadata -- synthesize a stub so callers
            # never have to special-case "totally unknown command".
            return CommandSpec(cmd_set=cmd_set, cmd_id=cmd_id,
                                name=f'Unregistered_0x{cmd_id:02X}',
                                decode_status='none', fields=None)
        return spec

    def find_by_name(self, name: str) -> List[CommandSpec]:
        """Case-insensitive substring search over command names."""
        name = name.lower()
        out = []
        for key, specs in self._by_name.items():
            if name in key:
                out.extend(specs)
        return out

    def all(self) -> List[CommandSpec]:
        return list(self._by_key.values())

    def by_cmd_set(self, cmd_set: int) -> List[CommandSpec]:
        return sorted((s for s in self._by_key.values() if s.cmd_set == cmd_set),
                      key=lambda s: s.cmd_id)

    def stats(self) -> dict:
        total = len(self._by_key)
        full = sum(1 for s in self._by_key.values() if s.decode_status == 'full')
        return {'total': total, 'full': full, 'none': total - full}


# module-level singleton for convenience
_default_registry: Optional[CommandRegistry] = None


def default_registry() -> CommandRegistry:
    global _default_registry
    if _default_registry is None:
        _default_registry = CommandRegistry()
    return _default_registry

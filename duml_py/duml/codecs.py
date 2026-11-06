"""
Payload field codec: turns a command's `fields` spec (as stored in
commands.json, derived from the Wireshark dissector source -- see
../../DUML_PROTOCOL/README.md for how) into actual encode()/decode()
of payload bytes.

Design notes
------------
A command's `fields` list is a flat sequence of (offset, size, type, mask,
branch) entries, exactly mirroring how the source Lua dissector calls
`subtree:add(f.name, payload(offset, size))` in order. This module turns
that back into something usable for real traffic:

* Fields that share the same `offset` are bitfield siblings of one
  underlying integer (e.g. a byte split into 3 flag bits) -- they are
  grouped into a single "slot" and combined/split via each field's `mask`.
* Fields tagged with a `branch` (e.g. ``"if pack_type == 0 then"`` for a
  Request-only field, or ``"if (payload:len() >= 6) then"`` for an optional
  tail) are grouped by branch text into alternative/optional field sets.
  Decoding picks the branch whose declared byte range actually fits the
  payload length given (falling back to the smallest-declared-length
  branch, mirroring the "try biggest struct that fits" pattern already
  used by dji-firmware-tools' own comm_mkdupc.py). Encoding requires the
  caller to pick a branch explicitly via `variant=` when more than one
  exists (unambiguous single-branch commands need no `variant`).
"""
from __future__ import annotations

import struct
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

FIXED_TYPE_SIZES = {
    'uint8': 1, 'int8': 1, 'uint16': 2, 'int16': 2, 'uint24': 3,
    'uint32': 4, 'int32': 4, 'uint64': 8, 'int64': 8,
    'float': 4, 'double': 8, 'ether': 6,
}


class CodecError(ValueError):
    pass


def _unpack_scalar(typ: str, raw: bytes) -> Any:
    if typ in ('uint8',):
        return raw[0]
    if typ in ('int8',):
        return struct.unpack('<b', raw)[0]
    if typ == 'uint16':
        return struct.unpack('<H', raw)[0]
    if typ == 'int16':
        return struct.unpack('<h', raw)[0]
    if typ == 'uint24':
        return int.from_bytes(raw, 'little', signed=False)
    if typ == 'uint32':
        return struct.unpack('<I', raw)[0]
    if typ == 'int32':
        return struct.unpack('<i', raw)[0]
    if typ == 'uint64':
        return struct.unpack('<Q', raw)[0]
    if typ == 'int64':
        return struct.unpack('<q', raw)[0]
    if typ == 'float':
        return struct.unpack('<f', raw)[0]
    if typ == 'double':
        return struct.unpack('<d', raw)[0]
    if typ == 'ether':
        return ':'.join(f'{b:02x}' for b in raw)
    if typ == 'string':
        return raw.split(b'\x00', 1)[0].decode('utf-8', errors='replace')
    # 'bytes', None, or anything unrecognized: return raw bytes untouched
    return bytes(raw)


def _pack_scalar(typ: str, value: Any, size: int) -> bytes:
    if typ == 'uint8':
        return bytes([int(value) & 0xFF])
    if typ == 'int8':
        return struct.pack('<b', int(value))
    if typ == 'uint16':
        return struct.pack('<H', int(value) & 0xFFFF)
    if typ == 'int16':
        return struct.pack('<h', int(value))
    if typ == 'uint24':
        return (int(value) & 0xFFFFFF).to_bytes(3, 'little')
    if typ == 'uint32':
        return struct.pack('<I', int(value) & 0xFFFFFFFF)
    if typ == 'int32':
        return struct.pack('<i', int(value))
    if typ == 'uint64':
        return struct.pack('<Q', int(value) & 0xFFFFFFFFFFFFFFFF)
    if typ == 'int64':
        return struct.pack('<q', int(value))
    if typ == 'float':
        return struct.pack('<f', float(value))
    if typ == 'double':
        return struct.pack('<d', float(value))
    if typ == 'ether':
        parts = bytes(int(x, 16) for x in str(value).split(':'))
        return parts.ljust(size, b'\x00')[:size]
    if typ == 'string':
        if isinstance(value, str):
            b = value.encode('utf-8')
        else:
            b = bytes(value)
        return b.ljust(size, b'\x00')[:size]
    # 'bytes' / unknown: caller supplies raw bytes (or an int for small sizes)
    if isinstance(value, int):
        return value.to_bytes(size, 'little')
    b = bytes(value)
    return b.ljust(size, b'\x00')[:size]


def _mask_shift(mask: Optional[int]) -> int:
    if not mask:
        return 0
    m = mask
    shift = 0
    while m and not (m & 1):
        m >>= 1
        shift += 1
    return shift


@dataclass
class FieldSlot:
    offset: int
    size: int
    members: List[dict]   # the raw field dicts sharing this offset


def _branch_matches_len(branch: str, payload_len: int) -> Optional[bool]:
    """Evaluate a `payload:len() >= N` / `payload:len() <= N` branch text
    against a concrete payload length. Returns None if the branch text
    isn't a length-based condition (caller should try other strategies)."""
    import re
    m = re.search(r'payload:len\(\)\s*(>=|<=|==|>|<)\s*(\d+)', branch)
    if not m:
        return None
    op, n = m.group(1), int(m.group(2))
    if op == '>=': return payload_len >= n
    if op == '<=': return payload_len <= n
    if op == '==': return payload_len == n
    if op == '>':  return payload_len > n
    if op == '<':  return payload_len < n
    return None


def _group_by_branch(fields: List[dict]) -> Dict[Optional[str], List[dict]]:
    groups: Dict[Optional[str], List[dict]] = {}
    for f in fields:
        groups.setdefault(f.get('branch'), []).append(f)
    return groups


def _group_into_slots(fields: List[dict]) -> List[FieldSlot]:
    slots: Dict[Tuple[int, int], FieldSlot] = {}
    order: List[Tuple[int, int]] = []
    for f in fields:
        key = (f['offset'], f['size'])
        if key not in slots:
            slots[key] = FieldSlot(offset=f['offset'], size=f['size'], members=[])
            order.append(key)
        slots[key].members.append(f)
    return [slots[k] for k in order]


def select_branch(fields: List[dict], payload_len: int,
                   packet_type: Optional[int] = None,
                   variant: Optional[str] = None) -> List[dict]:
    """Return the flat list of (unconditional + chosen-branch) fields that
    should be applied for a payload of the given length / direction."""
    groups = _group_by_branch(fields)
    base = groups.pop(None, [])
    if not groups:
        return base

    if variant is not None:
        for label in groups:
            if label and variant in label:
                return base + groups[label]
        raise CodecError(f"no branch matching variant={variant!r}; available: {list(groups)}")

    # direction-based (Request/Response) selection
    if packet_type is not None:
        want = 'pack_type == 0' if packet_type == 0 else 'pack_type == 1'
        for label in groups:
            if label and want in label:
                return base + groups[label]
        for label in groups:
            if label and (('Request' in label and packet_type == 0) or
                           ('Response' in label and packet_type == 1)):
                return base + groups[label]

    # length-based selection: evaluate each branch's own condition if it's
    # a payload:len() check; otherwise fall back to "does it fit" sizing.
    candidates = []
    for label, flds in groups.items():
        if label:
            m = _branch_matches_len(label, payload_len)
            if m is True:
                candidates.append((0, label, flds))
                continue
            if m is False:
                continue
        max_end = max((f['offset'] + (f['size'] or 0) for f in flds), default=0)
        fits = max_end <= payload_len
        candidates.append((0 if fits else 1, label, flds))
    if not candidates:
        return base
    candidates.sort(key=lambda c: c[0])
    best_rank = candidates[0][0]
    # Among equally-good candidates, prefer the one whose max offset+size is
    # largest but still <= payload_len (closest fit, biggest-struct-that-fits).
    best = [c for c in candidates if c[0] == best_rank]
    def _span(flds):
        return max((f['offset'] + (f['size'] or 0) for f in flds), default=0)
    best.sort(key=lambda c: _span(c[2]), reverse=True)
    return base + best[0][2]


def decode_payload(fields: Optional[List[dict]], payload: bytes,
                    packet_type: Optional[int] = None,
                    variant: Optional[str] = None) -> Dict[str, Any]:
    """Decode `payload` according to `fields`. Returns a flat dict of
    field_name -> decoded value. If `fields` is None/empty, returns
    {'raw': payload} (nothing known about this command's structure)."""
    if not fields:
        return {'raw': payload}

    chosen = select_branch(fields, len(payload), packet_type=packet_type, variant=variant)
    out: Dict[str, Any] = {}
    for slot in _group_into_slots(chosen):
        end = slot.offset + slot.size
        if end > len(payload):
            continue
        raw_bytes = payload[slot.offset:end]
        if len(slot.members) == 1 and not slot.members[0].get('mask'):
            f = slot.members[0]
            out[f['name']] = _unpack_scalar(f.get('type') or 'bytes', raw_bytes)
            continue
        raw_int = int.from_bytes(raw_bytes, 'little')
        for f in slot.members:
            mask = f.get('mask')
            if mask:
                mv = int(mask, 0) if isinstance(mask, str) else mask
                shift = _mask_shift(mv)
                out[f['name']] = (raw_int & mv) >> shift
            else:
                out[f['name']] = raw_int
    return out


def encode_payload(fields: Optional[List[dict]], values: Dict[str, Any],
                    packet_type: Optional[int] = None,
                    variant: Optional[str] = None,
                    total_len: Optional[int] = None) -> bytes:
    """Encode `values` (field_name -> value) into payload bytes according
    to `fields`. Unspecified fields default to all-zero bytes. If `fields`
    is None/empty, `values['raw']` (bytes) is returned as-is -- this is how
    you send any command with no known structure: pass {'raw': b'...'}."""
    if not fields:
        raw = values.get('raw', b'')
        return bytes(raw)

    if total_len is None:
        # Infer which optional/length-gated branches the caller actually
        # wants included, from which field names they supplied values for
        # -- NOT by assuming the longest possible variant. Only fields the
        # caller explicitly set count; a branch nobody supplied values for
        # should not silently get padded into the output.
        provided = set(values.keys())
        present = [f for f in fields if f['name'] in provided]
        total_len = max((f['offset'] + (f['size'] or 0) for f in present), default=0)

    chosen = select_branch(fields, total_len, packet_type=packet_type, variant=variant)
    if not chosen:
        return b''
    span = max(f['offset'] + (f['size'] or 0) for f in chosen)
    buf = bytearray(span)

    for slot in _group_into_slots(chosen):
        if len(slot.members) == 1 and not slot.members[0].get('mask'):
            f = slot.members[0]
            if f['name'] in values:
                raw = _pack_scalar(f.get('type') or 'bytes', values[f['name']], slot.size)
                buf[slot.offset:slot.offset + slot.size] = raw
            continue
        # bitfield slot: start from an explicitly-given whole-slot value if
        # present (a field here with no mask acting as the "parent" byte),
        # else OR together the individually-given sub-fields.
        raw_int = 0
        whole = next((f for f in slot.members if not f.get('mask') and f['name'] in values), None)
        if whole is not None:
            raw_int = int(values[whole['name']])
        for f in slot.members:
            if f['name'] not in values:
                continue
            mask = f.get('mask')
            if not mask:
                continue
            mv = int(mask, 0) if isinstance(mask, str) else mask
            shift = _mask_shift(mv)
            raw_int = (raw_int & ~mv) | ((int(values[f['name']]) << shift) & mv)
        buf[slot.offset:slot.offset + slot.size] = raw_int.to_bytes(slot.size, 'little')

    return bytes(buf)

#!/usr/bin/env python3
"""
Generate duml_py/duml/commands.json from the parsed Lua dissector database
(duml_lua_db.json, itself produced by parse_lua.py from the actual
dji-firmware-tools Wireshark Lua source). This is the missing link in the
pipeline described in DUML_PROTOCOL/README.md (Lua dissector -> parse_lua.py
-> duml_lua_db.json -> [this script] -> commands.json -> duml_py/duml_c) --
previously that last step was done once, by hand, outside this repo.
Having it as a real script means a fix or addition made to the Lua
dissector source flows through to commands.json (and from there to
duml_c/generated/registry_data.cpp via gen_cpp_registry.py) automatically
by re-running the pipeline, instead of needing a parallel hand-edit.

Usage:
    python3 DUML_PROTOCOL/tools/parse_lua.py DUML_PROTOCOL/tools \
        /path/to/dji-firmware-tools/comm_dissector/wireshark/*.lua
    python3 DUML_PROTOCOL/tools/lua_db_to_commands_json.py \
        DUML_PROTOCOL/tools/duml_lua_db.json duml_py/duml/commands.json
"""
import json
import re
import sys

# cmd_set -> (lua file, CMD_TEXT table name, CMD_DISSECT table name) for the
# four cmd_sets split into their own file; everything else (0x01, 0x05-0x11)
# is defined directly inside dji-dumlv1-proto.lua, keyed through its own
# DJI_DUMLv1_CMD_TEXT / DJI_DUMLv1_CMD_DISSECT tables of table-NAMES.
FILES = {
    '0x00': ('dji-dumlv1-general.lua', 'GENERAL_UART_CMD_TEXT', 'GENERAL_UART_CMD_DISSECT'),
    '0x02': ('dji-dumlv1-camera.lua', 'CAMERA_UART_CMD_TEXT', 'CAMERA_UART_CMD_DISSECT'),
    '0x03': ('dji-dumlv1-flyc.lua', 'FLYC_UART_CMD_TEXT', 'FLYC_UART_CMD_DISSECT'),
    '0x04': ('dji-dumlv1-gimbal.lua', 'GIMBAL_UART_CMD_TEXT', 'GIMBAL_UART_CMD_DISSECT'),
}
CMD_SET_NAMES = {
    '0x00': 'General', '0x01': 'Special', '0x02': 'Camera', '0x03': 'Flight Control',
    '0x04': 'Gimbal', '0x05': 'Center Board', '0x06': 'Remote Control', '0x07': 'Wi-Fi',
    '0x08': 'DM36x', '0x09': 'HD Link', '0x0a': 'Mono/Binocular (Vision)',
    '0x0b': 'Simulator', '0x0c': 'ESC', '0x0d': 'Battery', '0x0e': 'Data Logger',
    '0x0f': 'RTK', '0x10': 'Automation', '0x11': 'ADSB',
}

FIXED_TYPE_SIZES = {
    'uint8': 1, 'int8': 1, 'uint16': 2, 'int16': 2, 'uint24': 3, 'int24': 3,
    'uint32': 4, 'int32': 4, 'uint64': 8, 'int64': 8, 'float': 4, 'double': 8,
    'ether': 6, 'bool': 1,
}
BUFEXPR_SIZE_RE = re.compile(r'payload\s*\(\s*[^,]+,\s*([^)]+)\)')


def get_source(db, proto, cmd_set_hex):
    if cmd_set_hex in FILES:
        fname, textkey, dissectkey = FILES[cmd_set_hex]
        src = db[fname]
        return src, src['cmd_text_tables'].get(textkey, {}), src['cmd_dissect_tables'].get(dissectkey, {})
    textname = proto['cmd_text_tables']['DJI_DUMLv1_CMD_TEXT'].get(cmd_set_hex)
    dissectname = proto['cmd_dissect_tables']['DJI_DUMLv1_CMD_DISSECT'].get(cmd_set_hex)
    text_tbl = proto['cmd_text_tables'].get(textname, {}) if textname else {}
    dissect_tbl = proto['cmd_dissect_tables'].get(dissectname, {}) if dissectname else {}
    return proto, text_tbl, dissect_tbl


def find_field_def(db, src, varname):
    f = src['fields'].get(varname)
    if f is not None:
        return f
    for other in db.values():
        if varname in other.get('fields', {}):
            return other['fields'][varname]
    return None


def split_top_level_commas(s):
    """Split on commas not inside a quoted string or (...)/{...} nesting."""
    parts, depth, in_str, cur = [], 0, False, []
    i = 0
    while i < len(s):
        c = s[i]
        if in_str:
            cur.append(c)
            if c == '"':
                in_str = False
        elif c == '"':
            in_str = True
            cur.append(c)
        elif c in '({':
            depth += 1
            cur.append(c)
        elif c in ')}':
            depth -= 1
            cur.append(c)
        elif c == ',' and depth == 0:
            parts.append(''.join(cur).strip())
            cur = []
        else:
            cur.append(c)
        i += 1
    if cur:
        parts.append(''.join(cur).strip())
    return parts


def parse_rest(rest):
    """ProtoField(...)'s trailing constructor args, in this codebase's
    consistent order: base, valuestring(enum table ref), mask, desc.
    Returns (enum, mask, desc), each None if 'nil' or absent."""
    if not rest:
        return None, None, None
    parts = split_top_level_commas(rest)
    enum_s = parts[1] if len(parts) > 1 else None
    mask_s = parts[2] if len(parts) > 2 else None
    desc_s = parts[3] if len(parts) > 3 else None
    enum = None
    if enum_s and enum_s != 'nil' and re.fullmatch(r'enums\.[A-Za-z0-9_]+', enum_s):
        enum = enum_s
    mask = None
    if mask_s and mask_s != 'nil' and re.fullmatch(r'0[xX][0-9A-Fa-f]+', mask_s):
        mask = mask_s
    desc = None
    if desc_s and desc_s != 'nil':
        m = re.fullmatch(r'"(.*)"', desc_s, re.S)
        if m:
            desc = m.group(1)
    return enum, mask, desc


def size_from_bufexpr(bufexpr):
    m = BUFEXPR_SIZE_RE.search(bufexpr or '')
    if not m:
        return None
    expr = m.group(1).strip()
    if re.fullmatch(r'-?\d+', expr):
        return int(expr)
    return None  # non-literal size expression (e.g. a variable) -- leave to caller


def try_eval_offset(expr, known):
    """Best-effort: resolve a simple integer literal or a previously-seen
    local variable; anything fancier (arithmetic on runtime values) is left
    as None, meaning 'offset unknown, not synthesizable from static parse'."""
    expr = expr.strip().rstrip(',')
    if re.fullmatch(r'-?\d+', expr):
        return int(expr)
    return known.get(expr)


def walk_function(fn):
    """Replay a parsed dissector function's event stream into an ordered
    field list with concrete offsets, same shape as commands.json's 'fields'.
    Returns (fields_list, fully_resolved: bool)."""
    offset = 0
    offset_known = True
    fields = []
    branch_stack = []  # list of branch text strings, one per nesting level
    # Alternatives in an if/elseif/else chain parse the SAME bytes under
    # different length/condition assumptions -- they don't continue from
    # wherever a sibling alternative's fields would have left the offset.
    # Snapshot (offset, offset_known) when each 'if' is entered, and
    # restore it at every subsequent elseif/else *and* at the matching
    # 'end' (since statically we can't know which branch actually ran, so
    # anything after the whole chain can't reliably inherit either
    # branch's ending offset).
    offset_snapshot_stack = []
    fully_resolved = True

    def branch_label():
        # Innermost branch only (matches the existing commands.json
        # convention) -- outer context is implied by nesting, not spelled
        # out in the label.
        return branch_stack[-1] if branch_stack else None

    for ev in fn['events']:
        kind = ev['kind']
        if kind == 'offset_init':
            val = try_eval_offset(ev['expr'], {})
            if val is None:
                fully_resolved = False
                offset_known = False
            else:
                offset = val
                offset_known = True
        elif kind == 'offset_adv':
            if not offset_known:
                continue
            size = None
            if re.fullmatch(r'-?\d+', ev['expr'].strip()):
                size = int(ev['expr'].strip())
            if size is None:
                fully_resolved = False
                offset_known = False
            else:
                offset += size
        elif kind == 'if':
            offset_snapshot_stack.append((offset, offset_known))
            branch_stack.append(ev['text'].strip())
        elif kind == 'elseif':
            if offset_snapshot_stack:
                offset, offset_known = offset_snapshot_stack[-1]
            branch_stack.append(ev['text'].strip()) if not branch_stack else branch_stack.__setitem__(-1, ev['text'].strip())
        elif kind == 'else':
            if offset_snapshot_stack:
                offset, offset_known = offset_snapshot_stack[-1]
            if branch_stack:
                branch_stack[-1] = ev['text'].strip()
            else:
                branch_stack.append(ev['text'].strip())
        elif kind == 'end':
            if offset_snapshot_stack:
                offset, offset_known = offset_snapshot_stack.pop()
            if branch_stack:
                branch_stack.pop()
        elif kind == 'add':
            # Offset is advanced solely by explicit 'offset_adv' events (the
            # Lua source's own `offset = offset + N` lines) -- NOT here.
            # Auto-advancing here too would double-count, since every one
            # of these 'add' lines in practice is followed by its own
            # explicit offset_adv line for the same size.
            size = size_from_bufexpr(ev.get('bufexpr', ''))
            fields.append({
                'name': ev['field'],
                'offset': offset if offset_known else None,
                'size': size,
                'branch': branch_label(),
                'inline_comment': (ev.get('comment') or '').strip() or None,
                '_line': ev.get('line'),
            })
            if size is None:
                fully_resolved = False
    return fields, fully_resolved


def build_field_entry(db, src, raw_field):
    fdef = find_field_def(db, src, raw_field['name'])
    ptype = fdef['ptype'] if fdef else None
    # Lua ProtoField type names mostly match ours; a few need remapping.
    type_map = {'bytes': 'bytes', 'string': 'string', 'stringz': 'string',
                'framenum': 'uint32', 'guid': 'bytes', 'none': None}
    out_type = type_map.get(ptype, ptype)
    size = raw_field['size']
    if size is None and out_type in FIXED_TYPE_SIZES:
        size = FIXED_TYPE_SIZES[out_type]
    enum, mask, desc = parse_rest(fdef.get('rest')) if fdef else (None, None, None)
    return {
        'name': raw_field['name'],
        'label': fdef['label'] if fdef else raw_field['name'],
        'offset': raw_field['offset'],
        'size': size,
        'type': out_type if out_type not in (None,) else 'bytes',
        'enum': enum,
        'mask': mask,
        'desc': desc,
        'comment': raw_field.get('inline_comment'),
        'branch': raw_field['branch'],
    }


def main():
    db_path = sys.argv[1] if len(sys.argv) > 1 else 'duml_lua_db.json'
    out_path = sys.argv[2] if len(sys.argv) > 2 else 'commands.json'
    db = json.load(open(db_path))
    proto = db['dji-dumlv1-proto.lua']

    commands = []
    stats = {'full': 0, 'partial': 0, 'none': 0}
    for cmd_set_hex in [f'0x{i:02x}' for i in range(0x12)]:
        src, text_tbl, dissect_tbl = get_source(db, proto, cmd_set_hex)
        for cmd_id_hex, name in text_tbl.items():
            cmd_id = int(cmd_id_hex, 16)
            dissector_fn = dissect_tbl.get(cmd_id_hex)
            fields = None
            decode_status = 'none'
            if dissector_fn:
                fn = src.get('functions', {}).get(dissector_fn)
                if fn is None:
                    for other in db.values():
                        if dissector_fn in other.get('functions', {}):
                            fn = other['functions'][dissector_fn]
                            src_for_fields = other
                            break
                    else:
                        src_for_fields = src
                else:
                    src_for_fields = src
                if fn is not None:
                    raw_fields, fully_resolved = walk_function(fn)
                    if raw_fields:
                        fields = [build_field_entry(db, src_for_fields, rf) for rf in raw_fields]
                        for f in fields:
                            f.pop('_line', None) if '_line' in f else None
                        decode_status = 'full' if fully_resolved and all(
                            f['offset'] is not None and f['size'] is not None for f in fields
                        ) else 'partial'
            stats[decode_status if decode_status in stats else 'none'] = stats.get(decode_status, 0) + 1
            commands.append({
                'cmd_set': int(cmd_set_hex, 16),
                'cmd_set_name': CMD_SET_NAMES[cmd_set_hex],
                'cmd_id': cmd_id,
                'name': name if isinstance(name, str) else str(name),
                'decode_status': decode_status,
                'source': 'dissector' if dissector_fn else None,
                'dissector_fn': dissector_fn,
                'fields': fields,
            })

    commands.sort(key=lambda c: (c['cmd_set'], c['cmd_id']))
    with open(out_path, 'w') as fh:
        json.dump(commands, fh, indent=1)
    print(f"Wrote {out_path}: {len(commands)} commands "
          f"({stats.get('full', 0)} full, {stats.get('partial', 0)} partial, "
          f"{stats.get('none', 0)} name-only)", file=sys.stderr)


if __name__ == '__main__':
    main()

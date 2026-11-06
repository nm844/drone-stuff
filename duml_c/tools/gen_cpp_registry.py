#!/usr/bin/env python3
"""
Generate duml_c/generated/registry_data.cpp from duml_py/duml/commands.json.

This is the single source of truth for both language bindings: edit
commands.json (or regenerate it per DUML_PROTOCOL/README.md), then re-run
this script and the Python build_registry.py output stays in sync with the
C++ one.
"""
import json
import os
import sys

def esc(s):
    if s is None:
        return ""
    return str(s).replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n')

def mask_to_int(m):
    if m is None:
        return 0
    if isinstance(m, int):
        return m
    try:
        return int(m, 0)
    except Exception:
        return 0

def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'duml_py/duml/commands.json'
    out = sys.argv[2] if len(sys.argv) > 2 else 'duml_c/generated/registry_data.cpp'
    commands = json.load(open(src))
    commands.sort(key=lambda c: (c['cmd_set'], c['cmd_id']))

    lines = []
    lines.append('// GENERATED FILE -- do not hand-edit.')
    lines.append(f'// Produced by tools/gen_cpp_registry.py from {os.path.basename(src)}.')
    lines.append('// Regenerate instead of editing: see DUML_PROTOCOL/README.md for the')
    lines.append('// pipeline (Lua dissector -> commands.json -> this file).')
    lines.append('#include "duml/registry.hpp"')
    lines.append('')
    lines.append('namespace duml {')
    lines.append('')
    lines.append('namespace {')
    lines.append('')

    # Flatten all fields into one array; record (start, count) per command.
    all_fields = []
    spans = []  # (start, count) per command, in the same order as `commands`
    for c in commands:
        flds = c.get('fields') or []
        start = len(all_fields)
        for f in flds:
            all_fields.append(f)
        spans.append((start, len(flds)))

    lines.append(f'const Field kAllFields[{max(1, len(all_fields))}] = {{')
    for f in all_fields:
        name = esc(f['name'])
        label = esc(f.get('label'))
        offset = f.get('offset') if f.get('offset') is not None else 0
        size = f.get('size') if f.get('size') is not None else 0
        typ = esc(f.get('type'))
        enum = esc(f.get('enum'))
        mask = mask_to_int(f.get('mask'))
        desc = esc(f.get('desc'))
        branch = esc(f.get('branch'))
        lines.append(
            f'    {{"{name}", "{label}", {offset}, {size}, "{typ}", "{enum}", '
            f'{mask}u, "{desc}", "{branch}"}},'
        )
    lines.append('};')
    lines.append('')
    lines.append('} // namespace')
    lines.append('')

    lines.append(f'extern const CommandSpec kCommandTable[{len(commands)}] = {{')
    for c, (start, count) in zip(commands, spans):
        name = esc(c['name'])
        status = esc(c['decode_status'])
        source = esc(c.get('source'))
        dfn = esc(c.get('dissector_fn'))
        note = esc(c.get('note'))
        if count == 0:
            field_span = 'FieldSpan{nullptr, 0}'
        else:
            field_span = f'FieldSpan{{&kAllFields[{start}], {count}}}'
        lines.append(
            f'    {{{c["cmd_set"]}, {c["cmd_id"]}, "{name}", "{status}", '
            f'{field_span}, "{source}", "{dfn}", "{note}"}},'
        )
    lines.append('};')
    lines.append('')
    lines.append(f'extern const size_t kCommandTableSize = {len(commands)};')
    lines.append('')
    lines.append('} // namespace duml')
    lines.append('')

    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        f.write('\n'.join(lines))

    full = sum(1 for c in commands if c['decode_status'] == 'full')
    print(f"Wrote {out}: {len(commands)} commands ({full} full), {len(all_fields)} total fields",
          file=sys.stderr)

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
import json, re, os, sys

SCRATCH = '/private/tmp/claude-501/-Users-nick--claude-spares-spare-1FYbf3/08bc5580-acb2-4cce-9b1f-1709a640e783/scratchpad'
db = json.load(open(os.path.join(SCRATCH, 'duml_lua_db.json')))

proto = db['dji-dumlv1-proto.lua']
FILES = {
    '0x00': ('dji-dumlv1-general.lua', 'GENERAL_UART_CMD_TEXT', 'GENERAL_UART_CMD_DISSECT'),
    '0x02': ('dji-dumlv1-camera.lua', 'CAMERA_UART_CMD_TEXT', 'CAMERA_UART_CMD_DISSECT'),
    '0x03': ('dji-dumlv1-flyc.lua', 'FLYC_UART_CMD_TEXT', 'FLYC_UART_CMD_DISSECT'),
    '0x04': ('dji-dumlv1-gimbal.lua', 'GIMBAL_UART_CMD_TEXT', 'GIMBAL_UART_CMD_DISSECT'),
}
# All other cmd_sets (0x01, 0x05..0x11) are defined directly inside proto.lua
CMD_SET_NAMES = {
 '0x00':'General','0x01':'Special','0x02':'Camera','0x03':'Flight Control','0x04':'Gimbal',
 '0x05':'Center Board','0x06':'Remote Control','0x07':'Wi-Fi','0x08':'DM36x','0x09':'HD Link',
 '0x0a':'Mono/Binocular (Vision)','0x0b':'Simulator','0x0c':'ESC','0x0d':'Battery',
 '0x0e':'Data Logger','0x0f':'RTK','0x10':'Automation','0x11':'ADSB',
}

def get_source(cmd_set):
    if cmd_set in FILES:
        fname, textkey, dissectkey = FILES[cmd_set]
        src = db[fname]
        return src, src['cmd_text_tables'].get(textkey, {}), src['cmd_dissect_tables'].get(dissectkey, {})
    else:
        # lives in proto.lua: find table names from proto cmd_text_tables/cmd_dissect_tables
        textname = proto['cmd_text_tables']['DJI_DUMLv1_CMD_TEXT'][cmd_set]
        dissectname = proto['cmd_dissect_tables']['DJI_DUMLv1_CMD_DISSECT'][cmd_set]
        return proto, proto['cmd_text_tables'].get(textname, {}), proto['cmd_dissect_tables'].get(dissectname, {})

def field_info(src, varname):
    f = src['fields'].get(varname)
    if f is None:
        # search other files too (some dissectors reference fields defined elsewhere, e.g. proto.lua generic fields)
        for fname, d in db.items():
            if varname in d['fields']:
                return d['fields'][varname]
        return None
    return f

def parse_rest(rest):
    """ Parse the 'rest' tail of a ProtoField(...) call: base, valuestring, mask, desc """
    # split top-level commas (rest has no nested parens typically for these fields)
    parts = []
    depth = 0
    cur = ''
    for c in rest:
        if c == '(' : depth += 1
        if c == ')' : depth -= 1
        if c == ',' and depth == 0:
            parts.append(cur); cur = ''
        else:
            cur += c
    if cur.strip(): parts.append(cur)
    parts = [p.strip() for p in parts]
    base = parts[0] if len(parts) > 0 else ''
    valuestring = parts[1] if len(parts) > 1 else ''
    mask = parts[2] if len(parts) > 2 else ''
    desc = parts[3] if len(parts) > 3 else ''
    return base, valuestring, mask.strip(), desc.strip().strip('"')

SIZE_FROM_PTYPE = {
    'uint8':1,'int8':1,'uint16':2,'int16':2,'uint32':4,'int32':4,'uint64':8,'int64':8,
    'float':4,'double':8,'ether':6,
}

def render_function(src, fname, out):
    fn = src['functions'].get(fname)
    if fn is None:
        # fall back: search all parsed files (cross-cmdset reuse of a dissector function)
        for fkey, d in db.items():
            if fname in d['functions']:
                fn = d['functions'][fname]
                src = d
                break
    if fn is None:
        out.append(f"  _(dissector function `{fname}` not found by parser — see Lua source directly)_\n")
        return
    offset = None
    branch_stack = []  # snapshots of offset-at-if, for elseif/else/endif restoration
    cur_label = None
    rows = []
    section_rows = []
    sections = []  # list of (label, rows)
    def flush_section():
        nonlocal section_rows, cur_label
        if section_rows:
            sections.append((cur_label, section_rows))
        section_rows = []

    for ev in fn['events']:
        k = ev['kind']
        if k == 'offset_init':
            try:
                offset = int(ev['expr'], 0)
            except Exception:
                offset = 0
        elif k == 'if':
            flush_section()
            cur_label = ev['text']
            branch_stack.append(offset)
        elif k in ('elseif','else'):
            flush_section()
            cur_label = ev['text']
            if branch_stack:
                offset = branch_stack[-1]
        elif k == 'endif':
            if branch_stack:
                branch_stack.pop()
        elif k == 'add':
            m = re.search(r'payload\(\s*([^,]+)\s*,\s*([^)]+)\)', ev['bufexpr'])
            size_expr = m.group(2).strip() if m else '?'
            field = ev['field']
            finfo = field_info(src, field)
            size = None
            try:
                size = int(size_expr, 0)
            except Exception:
                size = None
            label = ptype = basef = valuestring = mask = desc = ''
            if finfo:
                label = finfo['label']; ptype = finfo['ptype']
                basef, valuestring, mask, desc = parse_rest(finfo['rest'])
            comment = ev.get('comment','')
            off_str = f"{offset}" if offset is not None else "?"
            section_rows.append({
                'offset': off_str, 'size': size_expr, 'field': field, 'label': label,
                'ptype': ptype, 'valuestring': valuestring, 'mask': mask, 'desc': desc,
                'comment': comment,
            })
            # NOTE: do not advance offset here - an explicit 'offset_adv' event
            # (parsed from the source's own "offset = offset + N" line) follows
            # immediately after every add() in this codebase and is the sole
            # authority for advancing the cursor. Advancing here too would double-count.
        elif k == 'offset_adv':
            expr = ev['expr']
            try:
                v = int(expr, 0)
                if offset is not None:
                    offset += v
            except Exception:
                offset = None
    flush_section()
    for label, rows in sections:
        if label:
            out.append(f"  *{label.strip()}*\n")
        out.append("  | Off | Size | Field | Type | Notes |")
        out.append("  |---|---|---|---|---|")
        for r in rows:
            def ok(v):
                return v and v.strip() not in ('nil','', 'base.HEX', 'base.DEC')
            notes = []
            if ok(r['valuestring']): notes.append(f"enum:`{r['valuestring']}`")
            if ok(r['mask']): notes.append(f"mask:`{r['mask']}`")
            if ok(r['desc']): notes.append(r['desc'])
            if r['comment'].strip(): notes.append(f"// {r['comment'].strip()}")
            notes_s = '; '.join(notes)
            out.append(f"  | {r['offset']} | {r['size']} | `{r['field']}` ({r['label']}) | {r['ptype']} | {notes_s} |")
        out.append("")

def main():
    outdir = sys.argv[1]
    os.makedirs(outdir, exist_ok=True)
    index = []
    for cmd_set in sorted(CMD_SET_NAMES.keys()):
        src, text_tbl, dissect_tbl = get_source(cmd_set)
        setname = CMD_SET_NAMES[cmd_set]
        out = [f"# Cmd Set {cmd_set} — {setname}\n"]
        all_ids = sorted(set(list(text_tbl.keys()) + list(dissect_tbl.keys())),
                          key=lambda x: int(x,0))
        out.append(f"Total known command IDs: {len(all_ids)}\n")
        n_decoded = 0
        for cid in all_ids:
            name = text_tbl.get(cid, '(name unknown)')
            dissector_fn = dissect_tbl.get(cid)
            out.append(f"## 0x{int(cid,0):02X} — {name}\n")
            if dissector_fn:
                n_decoded += 1
                out.append(f"Payload decoder: `{dissector_fn}`\n")
                render_function(src, dissector_fn, out)
            else:
                out.append("_No byte-level payload decoder in source dissector (name-only / unparsed payload)._\n")
        index.append((cmd_set, setname, len(all_ids), n_decoded))
        fn_out = os.path.join(outdir, f"cmdset_{cmd_set.replace('0x','')}_{setname.replace(' ','_').replace('/','-')}.md")
        with open(fn_out, 'w') as f:
            f.write('\n'.join(out))
        print(f"{cmd_set} {setname}: {len(all_ids)} cmd ids, {n_decoded} with byte decoders -> {fn_out}", file=sys.stderr)

    with open(os.path.join(outdir, 'INDEX.md'), 'w') as f:
        f.write("# DUML Command Set Index\n\n| Cmd Set | Name | # Cmd IDs known | # with byte-level decoder |\n|---|---|---|---|\n")
        for cmd_set, setname, nids, ndec in index:
            f.write(f"| {cmd_set} | {setname} | {nids} | {ndec} |\n")

if __name__ == '__main__':
    main()

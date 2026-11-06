#!/usr/bin/env python3
"""
Parse DJI DUML v1 Wireshark Lua dissectors into a structured JSON database:
  - ProtoField definitions (name, wireshark type, display base, enum table ref, bitmask, description)
  - CMD_TEXT tables (cmd_set -> {cmd_id: name})
  - CMD_DISSECT tables (cmd_set -> {cmd_id: dissector_function_name})
  - dissector function bodies -> ordered list of (raw_line, field_ref, size_expr, comment)
This is a best-effort structural parse (regex-based), not a full Lua interpreter.
Branches (if/else, request/response) are preserved as annotated markers in sequence.
"""
import re, json, sys, glob, os

FIELD_DEF_RE = re.compile(
    r'''^\s*f\.(?P<varname>[A-Za-z0-9_]+)\s*=\s*ProtoField\.(?P<ptype>[A-Za-z0-9_]+)\s*\(\s*
        "(?P<wsname>[^"]+)"\s*,\s*"(?P<label>[^"]*)"\s*
        (?:,\s*(?P<rest>.*))?\)\s*$''', re.X)

FUNC_START_RE = re.compile(r'^\s*local\s+function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*$')
FUNC_START_RE2 = re.compile(r'^\s*function\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)\s*$')
ADD_RE = re.compile(r'subtree:add(?:_le)?\s*\(\s*f\.([A-Za-z0-9_]+)\s*,\s*([^)]*\))', re.X)
OFFSET_ADV_RE = re.compile(r'offset\s*=\s*offset\s*\+\s*(.+)$')
IF_RE = re.compile(r'^\s*(if|elseif|else|end)\b(.*)$')
CMD_TEXT_TABLE_RE = re.compile(r'^\s*(?:local\s+)?([A-Za-z0-9_]+_CMD_TEXT)\s*=\s*\{')
CMD_DISSECT_TABLE_RE = re.compile(r'^\s*(?:local\s+)?([A-Za-z0-9_]+_CMD_DISSECT)\s*=\s*\{')
TABLE_ENTRY_RE = re.compile(r'\[\s*(0x[0-9A-Fa-f]+|\d+)\s*\]\s*=\s*(.+?),?\s*(?:--.*)?$')
ENUM_DEF_RE = re.compile(r'^\s*enums\.([A-Za-z0-9_]+)\s*=\s*\{')

def strip_comment(line):
    # naive: remove -- comment not inside quotes (good enough for this codebase)
    out = []
    in_str = False
    i = 0
    while i < len(line):
        c = line[i]
        if c == '"' :
            in_str = not in_str
            out.append(c)
        elif not in_str and line[i:i+2] == '--':
            break
        else:
            out.append(c)
        i += 1
    return ''.join(out)

def parse_file(path):
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()

    fields = {}
    enums_tables = {}
    cmd_text_tables = {}
    cmd_dissect_tables = {}
    functions = {}  # name -> list of event dicts

    i = 0
    n = len(lines)
    while i < n:
        raw = lines[i]
        line = raw.rstrip('\n')
        stripped_nc = strip_comment(line)

        m = FIELD_DEF_RE.match(stripped_nc)
        if m:
            fields[m.group('varname')] = {
                'wsname': m.group('wsname'),
                'label': m.group('label'),
                'ptype': m.group('ptype'),
                'rest': (m.group('rest') or '').strip(),
                'line': i+1,
            }
            i += 1
            continue

        m = ENUM_DEF_RE.match(stripped_nc)
        if m:
            name = m.group(1)
            j = i+1
            entries = {}
            while j < n and not re.match(r'^\s*\}', lines[j]):
                em = TABLE_ENTRY_RE.search(strip_comment(lines[j]))
                if em:
                    entries[em.group(1)] = em.group(2).strip().strip("'\"")
                j += 1
            enums_tables[name] = entries
            i = j+1
            continue

        m = CMD_TEXT_TABLE_RE.match(stripped_nc)
        if m:
            name = m.group(1)
            j = i+1
            entries = {}
            while j < n and not re.match(r'^\s*\}', lines[j]):
                em = TABLE_ENTRY_RE.search(strip_comment(lines[j]))
                if em:
                    entries[em.group(1)] = em.group(2).strip().strip("'\"")
                j += 1
            cmd_text_tables[name] = entries
            i = j+1
            continue

        m = CMD_DISSECT_TABLE_RE.match(stripped_nc)
        if m:
            name = m.group(1)
            j = i+1
            entries = {}
            while j < n and not re.match(r'^\s*\}', lines[j]):
                em = TABLE_ENTRY_RE.search(strip_comment(lines[j]))
                if em:
                    entries[em.group(1)] = em.group(2).strip().rstrip(',')
                j += 1
            cmd_dissect_tables[name] = entries
            i = j+1
            continue

        m = FUNC_START_RE.match(line) or FUNC_START_RE2.match(line)
        if m:
            fname = m.group(1)
            args = m.group(2)
            j = i+1
            depth = 1
            events = []
            while j < n and depth > 0:
                fl = lines[j]
                sfl = strip_comment(fl)
                # track end/if nesting roughly via keywords at line start
                if re.search(r'\bend\b\s*$', sfl.strip()) and not re.search(r'\b(if|for|while|function)\b', sfl):
                    depth -= 1
                    if depth == 0:
                        j += 1
                        break
                if re.match(r'^\s*(if)\b.*\bthen\s*$', sfl):
                    events.append({'kind':'if', 'text': sfl.strip(), 'line': j+1})
                elif re.match(r'^\s*elseif\b.*\bthen\s*$', sfl):
                    events.append({'kind':'elseif', 'text': sfl.strip(), 'line': j+1})
                elif re.match(r'^\s*else\s*$', sfl):
                    events.append({'kind':'else', 'text': sfl.strip(), 'line': j+1})
                elif re.match(r'^\s*end\s*$', sfl):
                    events.append({'kind':'endif', 'text': '', 'line': j+1})
                am = ADD_RE.search(sfl)
                if am:
                    fieldname, bufexpr = am.group(1), am.group(2)
                    events.append({'kind':'add', 'field': fieldname, 'bufexpr': bufexpr, 'line': j+1,
                                   'comment': fl.split('--',1)[1].strip() if '--' in fl else ''})
                om = OFFSET_ADV_RE.search(sfl)
                plain_reinit = re.match(r'^\s*offset\s*=\s*([0-9][0-9xXa-fA-F]*)\s*$', sfl)
                if om:
                    events.append({'kind':'offset_adv', 'expr': om.group(1).strip(), 'line': j+1})
                elif plain_reinit:
                    events.append({'kind':'offset_init', 'expr': plain_reinit.group(1).strip(), 'line': j+1})
                lom = re.search(r'local\s+offset\s*=\s*(\S+)', sfl)
                if lom:
                    events.append({'kind':'offset_init', 'expr': lom.group(1).strip().rstrip(','), 'line': j+1})
                j += 1
            functions[fname] = {'args': args, 'events': events, 'start_line': i+1, 'end_line': j}
            i = j
            continue

        i += 1

    return {
        'fields': fields,
        'enums': enums_tables,
        'cmd_text_tables': cmd_text_tables,
        'cmd_dissect_tables': cmd_dissect_tables,
        'functions': functions,
    }

def main():
    outdir = sys.argv[1] if len(sys.argv) > 1 else '.'
    base = os.path.dirname(os.path.abspath(__file__))
    files = sys.argv[2:] if len(sys.argv) > 2 else None
    db = {}
    paths = files or sorted(glob.glob(os.path.join(os.getcwd(), '*.lua')))
    for p in paths:
        key = os.path.basename(p)
        db[key] = parse_file(p)
        nf = len(db[key]['fields'])
        nfn = len(db[key]['functions'])
        print(f"{key}: {nf} fields, {nfn} functions, "
              f"{len(db[key]['cmd_text_tables'])} CMD_TEXT tables, "
              f"{len(db[key]['cmd_dissect_tables'])} CMD_DISSECT tables", file=sys.stderr)
    with open(os.path.join(outdir, 'duml_lua_db.json'), 'w') as f:
        json.dump(db, f, indent=1)
    print("Wrote", os.path.join(outdir, 'duml_lua_db.json'), file=sys.stderr)

if __name__ == '__main__':
    main()

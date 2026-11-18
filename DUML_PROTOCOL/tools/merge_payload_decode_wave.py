#!/usr/bin/env python3
"""
Merge one payload-decode sweep Workflow's result JSON into duml_py/duml/commands.json.

For each command in the wave's `all_commands` list:
- status == "decoded" AND present in the wave's `verified` list (survived
  3-way adversarial reverify): sets decode_status="full", source="binary_re",
  dissector_fn (free-text handler description), and fields.
- otherwise (status == "insufficient_evidence" or "no_payload", or
  "decoded" but refuted on reverify): sets a human-readable `note` field
  from the command's own scenario_description/handler_evidence, so the
  real research effort is preserved instead of leaving the entry looking
  untouched. decode_status is left as "none" -- nothing was actually decoded.
  IMPORTANT: a "decoded but refuted" command had its HANDLER correctly
  identified (the reviewers confirmed the function/address itself) -- what
  failed adversarial review was the specific byte-offset/size/type claims
  for its fields, not the handler lookup. The note text says this
  explicitly for that case rather than the generic "no decoder found"
  framing, which would misrepresent a real handler-identification success
  as a total miss.

Does NOT touch registry_data.cpp/ALL_COMMANDS.csv/test counts -- regenerate
those separately with gen_cpp_registry.py / export_master_list.py after
running this, and bump test_registry.cpp's expected `full` count by hand
(the `total` count is unaffected, since no new (cmd_set,cmd_id) rows are
added -- this script only enriches existing "none" rows in place).

Usage:
    python3 DUML_PROTOCOL/tools/merge_payload_decode_wave.py \
        <wave_output.json> <default_cmd_set_decimal_or_omit>
"""
import json
import sys

COMMANDS_PATH = 'duml_py/duml/commands.json'
NOTE_DOC_REF = "See DUML_PROTOCOL/21_PAYLOAD_DECODE_SWEEP_FINDINGS.md for full search methodology."


def build_note(cmd, was_refuted_decode=False):
    # scenario_description is written reliably for "decoded" commands (it's
    # the worked example's scenario), but investigating agents don't always
    # fill it in for insufficient_evidence/no_payload commands -- handler_evidence
    # is where the real research detail (e.g. a newly-found subsystem) usually
    # lives instead. Prefer scenario_description when present (it's a cleaner
    # plain-English summary); fall back to handler_evidence rather than losing
    # the research entirely. Found and fixed after the General-wave (cmd_set
    # 0x00) digestion initially lost a real "Param Manager" subsystem finding
    # this way -- see 21_PAYLOAD_DECODE_SWEEP_FINDINGS.md.
    scenario = (cmd.get('scenario_description') or '').strip()
    if not scenario:
        scenario = (cmd.get('handler_evidence') or '').strip()
    status = cmd['status']
    if status == 'no_payload':
        tail = f"Confirmed no meaningful payload. {NOTE_DOC_REF}"
    elif was_refuted_decode:
        handler = cmd.get('handler_function') or cmd.get('handler_binary') or 'a handler'
        tail = (f"Handler correctly identified ({handler}), but the proposed field-layout "
                f"(offsets/sizes/types) did not survive 3-way adversarial reverify -- refuted, "
                f"not just unfound. {NOTE_DOC_REF}")
    else:
        tail = f"No aircraft-side decoder found despite exhaustive search. {NOTE_DOC_REF}"
    if scenario:
        return f"{scenario} {tail}"
    return tail


def main():
    wave_path = sys.argv[1]
    default_cmd_set = int(sys.argv[2]) if len(sys.argv) > 2 else None

    wave = json.load(open(wave_path))
    result = wave.get('result', wave)
    all_commands = result['all_commands']
    verified_keys = set()
    for v in result.get('verified', []):
        cs = v.get('cmd_set_hex')
        cs_int = int(cs, 16) if cs else default_cmd_set
        verified_keys.add((cs_int, int(v['cmd_id_hex'], 16)))
    refuted_keys = set()
    for v in result.get('refuted', []):
        cs = v.get('cmd_set_hex')
        cs_int = int(cs, 16) if cs else default_cmd_set
        refuted_keys.add((cs_int, int(v['cmd_id_hex'], 16)))

    commands = json.load(open(COMMANDS_PATH))
    by_key = {(c['cmd_set'], c['cmd_id']): c for c in commands}

    decoded_applied, notes_applied, skipped = 0, 0, 0
    for cmd in all_commands:
        cs_hex = cmd.get('cmd_set_hex')
        cmd_set = int(cs_hex, 16) if cs_hex else default_cmd_set
        if cmd_set is None:
            print(f"SKIP (no cmd_set): {cmd.get('cmd_id_hex')} {cmd.get('name')}", file=sys.stderr)
            skipped += 1
            continue
        cmd_id = int(cmd['cmd_id_hex'], 16)
        key = (cmd_set, cmd_id)
        entry = by_key.get(key)
        if entry is None:
            print(f"SKIP (not found in commands.json): cmd_set=0x{cmd_set:02x} cmd_id=0x{cmd_id:02x} {cmd.get('name')}", file=sys.stderr)
            skipped += 1
            continue

        if cmd['status'] == 'decoded' and key in verified_keys and cmd.get('fields'):
            entry['decode_status'] = 'full'
            entry['source'] = 'binary_re'
            handler_desc = cmd.get('handler_function') or cmd.get('handler_binary') or 'binary RE (see doc 21)'
            entry['dissector_fn'] = f"binary RE: {handler_desc}"
            fields = []
            for f in cmd['fields']:
                fields.append({
                    'name': f['name'], 'label': f['label'], 'offset': f['offset'],
                    'size': f['size'], 'type': f['type'], 'enum': None, 'mask': None,
                    'desc': f.get('desc') or f.get('enum_values') or None,
                    'comment': None, 'branch': None,
                })
            entry['fields'] = fields
            # Worked examples (request/response hex + explanation) are not part of
            # registry.py's/registry.hpp's loaded schema (dead weight if stored here) --
            # they go in the cmdset_XX_*.md doc by hand instead, where a human reads them.
            decoded_applied += 1
        else:
            entry['note'] = build_note(cmd, was_refuted_decode=(cmd['status'] == 'decoded' and key in refuted_keys))
            notes_applied += 1

    json.dump(commands, open(COMMANDS_PATH, 'w'), indent=1)
    with open(COMMANDS_PATH, 'a') as f:
        f.write('\n')
    print(f"Applied: {decoded_applied} decoded, {notes_applied} notes, {skipped} skipped", file=sys.stderr)


if __name__ == '__main__':
    main()

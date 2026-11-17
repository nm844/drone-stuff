#!/usr/bin/env python3
"""
Export duml_py/duml/commands.json into one flat master list: every known
DUML command across all cmd_sets, with its typical sender/receiver device
and a compact payload-field breakdown where one is known.

Sender/receiver note: DUML's sender_type/receiver_type are frame-level
fields (frame bytes 4-5), not fixed per-command metadata -- a given
cmd_set/cmd_id pair doesn't have one fixed sender, only a typical *request
target* (which chip handles that cmd_set) and the fact that a Response
frame simply swaps sender/receiver relative to the Request that triggered
it. What's below is that typical association (CMD_SET_TYPICAL_RECEIVER in
duml/enums.py, itself derived from the public dissector's per-cmd_set
routing, cross-checked against this repo's own firmware disassembly for
the frame codec -- see 00_FRAME_FORMAT.md), not a guarantee for every
individual command. The real sender on the wire for a REQUEST is whichever
host issued it -- APP (phone/tablet running DJI Fly/GO), PC (DJI Assistant
2), or RC relaying one of those -- and that is not recoverable from the
command definition alone.

Usage:
    python3 DUML_PROTOCOL/tools/export_master_list.py \
        > DUML_PROTOCOL/ALL_COMMANDS.csv
"""
import csv
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COMMANDS_JSON = os.path.join(HERE, '..', '..', 'duml_py', 'duml', 'commands.json')

TYPICAL_RECEIVER_NAME = {
    0x00: 'Any (varies by target chip)', 0x01: 'Flight Controller', 0x02: 'Camera',
    0x03: 'Flight Controller', 0x04: 'Gimbal', 0x05: 'Center Board',
    0x06: 'Remote Control', 0x07: 'Wi-Fi (air)', 0x08: 'DM36x (air)',
    0x09: 'HD-Link MCU (air)', 0x0a: 'Mono/Binocular (Vision)', 0x0b: 'Simulator',
    0x0c: 'ESC (proxied via Center Board -- see note)', 0x0d: 'Battery',
    0x0e: 'Any', 0x0f: 'GPS/RTK', 0x10: 'Any (no public commands catalogued yet)',
    0x11: 'Any',
    0x22: 'Any (dji_sys, multiple board variants -- binary-confirmed, not from a public dissector)',
    0x23: 'Any (camera-pipeline DSP-arbitration participants -- ss_dsp_manager, libhyperlapse_eis.so -- binary-confirmed, not from a public dissector)',
    0x51: 'Any (framework built-in, libduml_frwk.so -- binary-confirmed, not from a public dissector)',
}

# Per-(cmd_set, cmd_id) overrides of the two tables above, for cases where a
# single cmd_set-level receiver/sender label is wrong for one specific
# command within that cmd_set (e.g. cmd_set 0x22 "Demo Mode" is mostly a
# dji_sys feature, but 4 of its 5 known cmd_ids were binary-confirmed inside
# dji_flight instead -- see 04_WM260_DAEMON_FINDINGS.md and
# 14_FOLLOWUP_DEEPDIVE_FINDINGS.md Track H).
TYPICAL_RECEIVER_OVERRIDE = {
    (0x22, 0x06): 'dji_flight (binary-confirmed via an R_ARM_RELATIVE-backed .data array at vaddr 0xae0f8, not a public dissector)',
    (0x22, 0x07): 'dji_flight (binary-confirmed via an R_ARM_RELATIVE-backed .data array at vaddr 0xae0f8, not a public dissector)',
    (0x22, 0x08): 'dji_flight (binary-confirmed via an R_ARM_RELATIVE-backed .data array at vaddr 0xae0f8, not a public dissector)',
    (0x22, 0x44): 'dji_flight (binary-confirmed via an R_ARM_RELATIVE-backed .data array at vaddr 0xae0f8, not a public dissector)',
}
TYPICAL_REQUEST_SENDER_OVERRIDE = {
    (0x22, 0x06): 'internal/unresolved (registration-table entry confirmed; no caller or wire trigger path traced)',
    (0x22, 0x07): 'internal/unresolved (registration-table entry confirmed; no caller or wire trigger path traced)',
    (0x22, 0x08): 'internal/unresolved (registration-table entry confirmed; no caller or wire trigger path traced)',
    (0x22, 0x44): 'internal/unresolved (registration-table entry confirmed; no caller or wire trigger path traced)',
}

# Typical REQUEST-side sender for each cmd_set: the controlling host that
# would plausibly issue it. This is inference from what each cmd_set's
# commands *do* (e.g. "Gimbal Control" is issued by whatever is flying the
# aircraft), not something recovered from firmware -- flagged as such in
# the "sender_basis" column.
TYPICAL_REQUEST_SENDER_NAME = {
    0x00: 'APP / PC / RC (general housekeeping, varies)', 0x01: 'APP / PC',
    0x02: 'APP / RC', 0x03: 'APP / RC / PC', 0x04: 'APP / RC', 0x05: 'internal (FC/PMU)',
    0x06: 'APP / PC', 0x07: 'APP / PC', 0x08: 'internal (air link)', 0x09: 'internal (air link)',
    0x0a: 'Flight Controller', 0x0b: 'PC (DJI Assistant simulator mode)',
    0x0c: 'Center Board (proxy)', 0x0d: 'Flight Controller / PC', 0x0e: 'APP / PC',
    0x0f: 'Flight Controller', 0x10: 'APP (unknown -- no public commands)', 0x11: 'Flight Controller',
    0x22: 'internal (dji_sys, factory/demo-unit use suspected)',
    0x23: 'internal (camera-pipeline peer process arbitrating DSP ownership)',
    0x51: 'internal (framework/system)',
}


def field_summary(fields):
    if not fields:
        return ''
    parts = []
    for f in fields:
        branch = f" [{f['branch']}]" if f.get('branch') else ''
        parts.append(f"{f['offset']}:{f['size']}:{f['type']}:{f['name']}{branch}")
    return ' | '.join(parts)


def main():
    with open(COMMANDS_JSON) as fh:
        commands = json.load(fh)

    writer = csv.writer(sys.stdout)
    writer.writerow([
        'cmd_set_hex', 'cmd_set_name', 'cmd_id_hex', 'cmd_id_dec', 'name',
        'decode_status', 'typical_receiver', 'typical_request_sender',
        'dissector_fn', 'num_fields', 'payload_fields (offset:size:type:name[branch])',
    ])
    for e in sorted(commands, key=lambda e: (e['cmd_set'], e['cmd_id'])):
        writer.writerow([
            f"0x{e['cmd_set']:02x}", e['cmd_set_name'],
            f"0x{e['cmd_id']:02x}", e['cmd_id'], e['name'], e['decode_status'],
            TYPICAL_RECEIVER_OVERRIDE.get((e['cmd_set'], e['cmd_id']),
                TYPICAL_RECEIVER_NAME.get(e['cmd_set'], 'unknown')),
            TYPICAL_REQUEST_SENDER_OVERRIDE.get((e['cmd_set'], e['cmd_id']),
                TYPICAL_REQUEST_SENDER_NAME.get(e['cmd_set'], 'unknown')),
            e.get('dissector_fn') or '',
            len(e['fields']) if e['fields'] else 0,
            field_summary(e['fields']),
        ])

    missing = sorted(set(range(0x12)) - {e['cmd_set'] for e in commands})
    print(f"# cmd_sets with zero catalogued commands: "
          f"{[hex(m) for m in missing]}", file=sys.stderr)
    full = sum(1 for e in commands if e['decode_status'] == 'full')
    print(f"# {len(commands)} commands total, {full} with full payload decode, "
          f"{len(commands) - full} name-only (sendable/receivable as raw bytes)",
          file=sys.stderr)


if __name__ == '__main__':
    main()

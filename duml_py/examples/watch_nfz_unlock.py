#!/usr/bin/env python3
"""
Example: watch a live DUML link for the Flight Control (cmd_set 0x03)
traffic relevant to No-Fly-Zones and the Assistant-Unlock handshake, print
it in human units, and optionally log every frame seen as JSON lines for
later offline analysis.

This exists because the aircraft decrypts its own firmware into RAM and
then talks this protocol in the clear -- so the live NFZ table and the
unlock handshake can be observed and decoded without needing to break any
firmware encryption. See ../../DUML_PROTOCOL/02_WM265_MAVIC3_NFZ_FINDINGS.md
for how that conclusion was reached.

Commands watched (cmd_set 0x03 "Flight Control"):

    0x08  Nofly Zone Set              (raw -- no field layout published)
    0x09  Nofly Status Get            flight_limit_area_state, action_event
    0x3F  Set NoFly Zone Data         lat/lon/radius/country/type/id, fragmented
    0x41  Upload Unlimit Areas        (raw -- no field layout published)
    0x42  FlyC Unlimit State          is_in_unlimit_area, unlimit_areas_enabled
    0x47  Enable Unlimit Areas        (raw -- no field layout published)
    0x61  FlyC Activation Info        app_id, app_level, app_version
    0x62  FlyC Activation Exec        (raw -- no field layout published)
    0xCD  Update Nofly Area           (raw -- no field layout published)
    0xCF  New Nofly Area Get          (raw -- no field layout published)
    0xDF  Assistant Unlock Handler    request: lock_state; response: status

Where to tap in: the aircraft's RC-debug/FC-debug UART, or a USB-serial
link DJI Assistant 2 itself uses, carries this cmd_set. A USB sniff of the
link between the app/RC and the aircraft while triggering an unlock, or
flying toward a restricted-zone boundary, is the way to actually see 0xDF
and 0x3F traffic -- this script only decodes, it doesn't know how to make
the aircraft send these on its own.

    python examples/watch_nfz_unlock.py --transport serial --port /dev/ttyUSB0
    python examples/watch_nfz_unlock.py --transport tcp --host 127.0.0.1 --port-num 9000 --log capture.jsonl
"""
import argparse
import json
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml import DumlClient, CmdSet

WATCHED_CMD_IDS = {
    0x08: 'Nofly Zone Set',
    0x09: 'Nofly Status Get',
    0x3F: 'Set NoFly Zone Data',
    0x41: 'Upload Unlimit Areas',
    0x42: 'FlyC Unlimit State',
    0x47: 'Enable Unlimit Areas',
    0x61: 'FlyC Activation Info',
    0x62: 'FlyC Activation Exec',
    0xCD: 'Update Nofly Area',
    0xCF: 'New Nofly Area Get',
    0xDF: 'Assistant Unlock Handler',
}


class NflyZoneTable:
    """Accumulates fragments from repeated 0x3F frames into one table.
    Per the field's own description, num_entries == 0 marks end of transfer."""

    def __init__(self):
        self.zones = []
        self._in_progress = False

    def feed(self, fields: dict) -> bool:
        """Returns True if this fragment completed the transfer."""
        n = fields.get('flyc_set_nofly_zone_data_num_entries', 0)
        if n == 0:
            done, self._in_progress = self._in_progress, False
            return done
        self._in_progress = True
        self.zones.append({
            'frag': fields.get('flyc_set_nofly_zone_data_frag_num'),
            'lat_deg': fields['flyc_nofly_zone_entry_latitude'] / 1_000_000,
            'lon_deg': fields['flyc_nofly_zone_entry_longitude'] / 1_000_000,
            'radius_m': fields['flyc_nofly_zone_entry_radius'],
            'country_code': fields['flyc_nofly_zone_entry_contry_code'],
            'type': fields['flyc_nofly_zone_entry_type'],
            'area_id': fields['flyc_nofly_zone_entry_id'],
        })
        return False

    def dump(self):
        for z in self.zones:
            print(f"      area_id={z['area_id']:>10}  type={z['type']}  "
                  f"country={z['country_code']}  radius={z['radius_m']}m  "
                  f"({z['lat_deg']:.6f}, {z['lon_deg']:.6f})")


def describe(df, table: NflyZoneTable) -> str:
    cmd_id = df.spec.cmd_id
    f = df.fields
    direction = 'RESP' if df.frame.packet_type else 'REQ '

    if cmd_id == 0x09:
        return (f"Nofly Status: area_state={f.get('flyc_flyc_forbid_status_flight_limit_area_state')} "
                f"action_event={f.get('flyc_flyc_forbid_status_dji_flight_limit_action_event')} "
                f"limit_space_num={f.get('flyc_flyc_forbid_status_limit_space_num')}")

    if cmd_id == 0x3F:
        done = table.feed(f)
        line = (f"NoFly zone entry: area_id={f['flyc_nofly_zone_entry_id']} "
                f"type={f['flyc_nofly_zone_entry_type']} "
                f"country={f['flyc_nofly_zone_entry_contry_code']} "
                f"radius={f['flyc_nofly_zone_entry_radius']}m "
                f"({f['flyc_nofly_zone_entry_latitude']/1e6:.6f}, "
                f"{f['flyc_nofly_zone_entry_longitude']/1e6:.6f})"
                if f.get('flyc_set_nofly_zone_data_num_entries', 0) != 0
                else "NoFly zone transfer END")
        if done:
            line += f"\n    -- table complete, {len(table.zones)} entries:\n"
            import io
            buf = io.StringIO()
            old = sys.stdout
            sys.stdout = buf
            table.dump()
            sys.stdout = old
            line += buf.getvalue()
            table.zones.clear()
        return line

    if cmd_id == 0x42:
        if 'flyc_flyc_unlimit_state_is_in_unlimit_area' in f:
            return (f"Unlimit state: in_unlimit_area={f['flyc_flyc_unlimit_state_is_in_unlimit_area']} "
                    f"action={f['flyc_flyc_unlimit_state_unlimit_areas_action']} "
                    f"enabled={f['flyc_flyc_unlimit_state_unlimit_areas_enabled']} "
                    f"size={f['flyc_flyc_unlimit_state_unlimit_areas_size']}")
        return f"UAV posture (long form, not unlimit-state): {f}"

    if cmd_id == 0x61:
        return (f"Activation info: app_id=0x{f['flyc_flyc_active_request_app_id']:08X} "
                f"app_level={f['flyc_flyc_active_request_app_level']} "
                f"app_version={f['flyc_flyc_active_request_app_version']}")

    if cmd_id == 0xDF:
        if 'flyc_assistant_unlock_lock_state' in f:
            return f"Assistant Unlock {direction}: lock_state=0x{f['flyc_assistant_unlock_lock_state']:08X}"
        return f"Assistant Unlock {direction}: status={f.get('flyc_assistant_unlock_status')}"

    # Name-only commands: no published field layout, show raw payload.
    return f"{direction} raw payload ({len(df.frame.payload)} bytes): {df.frame.payload.hex()}"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--transport', choices=['serial', 'tcp'], required=True)
    ap.add_argument('--port')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port-num', type=int, default=9000)
    ap.add_argument('--duration', type=float, default=None, help='seconds, default forever')
    ap.add_argument('--all', action='store_true',
                     help='also print every other (non-Flight-Control-NFZ) frame seen')
    ap.add_argument('--log', help='append every watched frame as a JSON line to this file')
    args = ap.parse_args()

    if args.transport == 'serial':
        from duml.transport import SerialTransport
        transport = SerialTransport(args.port, baudrate=args.baud)
    else:
        from duml.transport import TcpTransport
        transport = TcpTransport(args.host, args.port_num)

    client = DumlClient(transport)
    table = NflyZoneTable()
    logf = open(args.log, 'a') if args.log else None

    print(f"Watching for Flight Control NFZ/Unlock traffic "
          f"(cmd_ids {', '.join(hex(c) for c in WATCHED_CMD_IDS)})...", file=sys.stderr)
    try:
        for df in client.listen(duration=args.duration):
            is_watched = (df.spec.cmd_set == int(CmdSet.FLIGHT_CONTROL)
                          and df.spec.cmd_id in WATCHED_CMD_IDS)
            if is_watched:
                ts = time.time()
                print(f"[{time.strftime('%H:%M:%S', time.localtime(ts))}] "
                      f"0x{df.spec.cmd_id:02X} {WATCHED_CMD_IDS[df.spec.cmd_id]}: "
                      f"{describe(df, table)}")
                if logf:
                    logf.write(json.dumps({
                        'ts': ts, 'cmd_id': df.spec.cmd_id, 'name': df.spec.name,
                        'direction': 'response' if df.frame.packet_type else 'request',
                        'fields': {k: (v.hex() if isinstance(v, bytes) else v)
                                   for k, v in df.fields.items()},
                        'raw_payload_hex': df.frame.payload.hex(),
                    }) + '\n')
                    logf.flush()
            elif args.all:
                print(df)
    except KeyboardInterrupt:
        pass
    finally:
        if logf:
            logf.close()
        transport.close()


if __name__ == '__main__':
    main()

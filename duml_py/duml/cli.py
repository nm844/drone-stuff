#!/usr/bin/env python3
"""
Command-line tool for the duml package.

Examples
--------
List commands in a cmd_set::

    python -m duml.cli list --cmd-set 4

Show full detail (byte layout) for one command::

    python -m duml.cli show --cmd-set 4 --cmd-id 1

Decode a hex-encoded frame you captured elsewhere::

    python -m duml.cli decode 55 0d 04 33 0a 03 34 12 00 00 00 de 22

Send a command over serial (fields as name=value pairs, or --raw HEX for an
unknown/unstructured payload)::

    python -m duml.cli send --transport serial --port /dev/ttyUSB0 \\
        --cmd-set 4 --cmd-id 1 --receiver-type GIMBAL \\
        --field gimbal_control_unkn0=1024 --field gimbal_control_unkn1=1024 \\
        --field gimbal_control_unkn2=1024

Listen and pretty-print every decoded frame for 10 seconds::

    python -m duml.cli listen --transport tcp --host 127.0.0.1 --port 9000 --duration 10
"""
from __future__ import annotations

import argparse
import sys
from typing import Any, Dict

from .client import DumlClient
from .enums import DeviceType
from .frame import Frame
from .registry import default_registry


def _parse_value(s: str) -> Any:
    s = s.strip()
    if s.lower().startswith('0x'):
        return int(s, 16)
    if s.lower().startswith('b64:'):
        import base64
        return base64.b64decode(s[4:])
    if s.lower().startswith('hex:'):
        return bytes.fromhex(s[4:])
    try:
        return int(s)
    except ValueError:
        pass
    try:
        return float(s)
    except ValueError:
        pass
    return s


def _parse_device(s: str) -> int:
    try:
        return int(s, 0)
    except ValueError:
        return int(DeviceType[s.upper()])


def cmd_list(args: argparse.Namespace) -> None:
    reg = default_registry()
    specs = reg.by_cmd_set(args.cmd_set) if args.cmd_set is not None else reg.all()
    for s in sorted(specs, key=lambda s: (s.cmd_set, s.cmd_id)):
        flag = 'FULL ' if s.decode_status == 'full' else 'none '
        print(f"0x{s.cmd_set:02X}/0x{s.cmd_id:02X}  [{flag}]  {s.cmd_set_name:<24s} {s.name}")


def cmd_show(args: argparse.Namespace) -> None:
    reg = default_registry()
    spec = reg.get(args.cmd_set, args.cmd_id)
    if spec is None:
        print(f"No registry entry for cmd_set=0x{args.cmd_set:02X} cmd_id=0x{args.cmd_id:02X} "
              "(it's still sendable/receivable -- just unnamed/raw).")
        return
    print(spec)
    if spec.note:
        print("Note:", spec.note)
    if not spec.fields:
        print("  (no known byte-level payload structure -- raw bytes only)")
        return
    for f in spec.fields:
        branch = f" [{f['branch']}]" if f.get('branch') else ""
        enum = f" enum={f['enum']}" if f.get('enum') else ""
        mask = f" mask={f['mask']}" if f.get('mask') else ""
        desc = f" -- {f['desc']}" if f.get('desc') else ""
        print(f"  off={f['offset']!s:>4} size={f['size']!s:>4} {f['type']!s:<8} "
              f"{f['name']}{mask}{enum}{branch}{desc}")


def cmd_decode(args: argparse.Namespace) -> None:
    data = bytes.fromhex(''.join(args.hex).replace(' ', ''))
    frame = Frame.decode(data, verify_crc=not args.no_verify)
    reg = default_registry()
    spec = reg.require(frame.cmd_set, frame.cmd_id)
    from .codecs import decode_payload
    fields = decode_payload(spec.fields, frame.payload, packet_type=frame.packet_type)
    print(f"Sender:   {DeviceType(frame.sender_type).name} (index {frame.sender_index})")
    print(f"Receiver: {DeviceType(frame.receiver_type).name} (index {frame.receiver_index})")
    print(f"Cmd Set:  0x{frame.cmd_set:02X} ({spec.cmd_set_name})")
    print(f"Cmd Id:   0x{frame.cmd_id:02X} ({spec.name})")
    print(f"Seq:      {frame.seq_num}")
    print(f"Type:     {'RESPONSE' if frame.packet_type else 'REQUEST'}  "
          f"Ack={frame.ack_type}  Encrypt={frame.encrypt_type}")
    print(f"Payload:  {frame.payload.hex()} ({len(frame.payload)} bytes)")
    if spec.decode_status == 'full':
        print("Decoded fields:")
        for k, v in fields.items():
            print(f"  {k} = {v!r}")
    else:
        print("  (payload structure unknown -- shown as raw bytes above)")


def _make_transport(args: argparse.Namespace):
    if args.transport == 'serial':
        from .transport import SerialTransport
        return SerialTransport(args.port, baudrate=args.baud)
    elif args.transport == 'tcp':
        from .transport import TcpTransport
        return TcpTransport(args.host, args.port_num)
    elif args.transport == 'tcp-server':
        from .transport import TcpServerTransport
        return TcpServerTransport(args.host, args.port_num)
    else:
        raise ValueError(args.transport)


def cmd_send(args: argparse.Namespace) -> None:
    transport = _make_transport(args)
    client = DumlClient(transport, sender_type=_parse_device(args.sender_type),
                         sender_index=args.sender_index)
    fields: Dict[str, Any] = {}
    for item in args.field or []:
        k, _, v = item.partition('=')
        fields[k] = _parse_value(v)
    raw_payload = bytes.fromhex(args.raw) if args.raw else None

    frame = client.build_frame(
        args.cmd_set, args.cmd_id,
        receiver_type=_parse_device(args.receiver_type),
        receiver_index=args.receiver_index,
        fields=fields, raw_payload=raw_payload,
        packet_type=args.packet_type, ack_type=args.ack_type,
        variant=args.variant,
    )
    print("Sending:", frame.encode().hex())
    client.send_frame(frame)
    if args.wait:
        print("Waiting for response...")
        resp = client.send_and_wait(args.cmd_set, args.cmd_id, timeout=args.timeout,
                                     receiver_type=_parse_device(args.receiver_type),
                                     fields=fields, raw_payload=raw_payload)
        print("Response:", resp)
    transport.close()


def cmd_listen(args: argparse.Namespace) -> None:
    transport = _make_transport(args)
    client = DumlClient(transport)
    try:
        for df in client.listen(duration=args.duration):
            print(df)
    finally:
        transport.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog='duml', description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='command', required=True)

    pl = sub.add_parser('list', help='list known commands')
    pl.add_argument('--cmd-set', type=lambda s: int(s, 0), default=None)
    pl.set_defaults(func=cmd_list)

    ps = sub.add_parser('show', help='show byte-level detail for one command')
    ps.add_argument('--cmd-set', type=lambda s: int(s, 0), required=True)
    ps.add_argument('--cmd-id', type=lambda s: int(s, 0), required=True)
    ps.set_defaults(func=cmd_show)

    pd = sub.add_parser('decode', help='decode a hex-encoded frame')
    pd.add_argument('hex', nargs='+', help='hex bytes, space or no separators')
    pd.add_argument('--no-verify', action='store_true', help='skip CRC validation')
    pd.set_defaults(func=cmd_decode)

    for name, fn in (('send', cmd_send), ('listen', cmd_listen)):
        sp = sub.add_parser(name, help=f'{name} over a live transport')
        sp.add_argument('--transport', choices=['serial', 'tcp', 'tcp-server'], required=True)
        sp.add_argument('--port', help='serial port, e.g. /dev/ttyUSB0 or COM3')
        sp.add_argument('--baud', type=int, default=115200)
        sp.add_argument('--host', default='127.0.0.1')
        sp.add_argument('--port-num', type=int, default=9000)
        if name == 'send':
            sp.add_argument('--cmd-set', type=lambda s: int(s, 0), required=True)
            sp.add_argument('--cmd-id', type=lambda s: int(s, 0), required=True)
            sp.add_argument('--sender-type', default='PC')
            sp.add_argument('--sender-index', type=int, default=0)
            sp.add_argument('--receiver-type', default='ANY')
            sp.add_argument('--receiver-index', type=int, default=0)
            sp.add_argument('--field', action='append', help='name=value, repeatable')
            sp.add_argument('--raw', help='hex bytes for an unstructured/unknown payload')
            sp.add_argument('--packet-type', type=int, default=0, choices=[0, 1])
            sp.add_argument('--ack-type', type=int, default=0, choices=[0, 1, 2])
            sp.add_argument('--variant', default=None, help='branch label substring, for commands with multiple payload shapes')
            sp.add_argument('--wait', action='store_true', help='wait for a response frame')
            sp.add_argument('--timeout', type=float, default=2.0)
        else:
            sp.add_argument('--duration', type=float, default=None)
        sp.set_defaults(func=fn)

    return p


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())

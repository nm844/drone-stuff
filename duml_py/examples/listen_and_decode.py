#!/usr/bin/env python3
"""
Example: listen on a transport and pretty-print every decoded DUML frame
seen, for every command the registry knows how to decode (and raw bytes
for the rest).

    python examples/listen_and_decode.py --transport serial --port /dev/ttyUSB0
    python examples/listen_and_decode.py --transport tcp --host 127.0.0.1 --port 9000
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml import DumlClient


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--transport', choices=['serial', 'tcp'], required=True)
    ap.add_argument('--port')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port-num', type=int, default=9000)
    ap.add_argument('--duration', type=float, default=None, help='seconds, default forever')
    args = ap.parse_args()

    if args.transport == 'serial':
        from duml.transport import SerialTransport
        transport = SerialTransport(args.port, baudrate=args.baud)
    else:
        from duml.transport import TcpTransport
        transport = TcpTransport(args.host, args.port_num)

    client = DumlClient(transport)
    try:
        for decoded in client.listen(duration=args.duration):
            print(decoded)
    except KeyboardInterrupt:
        pass
    finally:
        transport.close()


if __name__ == '__main__':
    main()

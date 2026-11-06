#!/usr/bin/env python3
"""
Example: send a Gimbal Control (cmd_set 0x04, cmd_id 0x01) command over a
serial link, centering pitch/roll/yaw. Adjust --port for your setup.

    python examples/send_gimbal_control.py --port /dev/ttyUSB0
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from duml import DumlClient, DeviceType
from duml.transport import SerialTransport


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--port', required=True)
    ap.add_argument('--baud', type=int, default=115200)
    args = ap.parse_args()

    transport = SerialTransport(args.port, baudrate=args.baud)
    client = DumlClient(transport, sender_type=int(DeviceType.APP))

    frame = client.send_command(
        0x04, 0x01,
        receiver_type=int(DeviceType.GIMBAL),
        fields={
            'gimbal_control_unkn0': 1024,  # mid-scale, per dissector's accepted 363..1685 range
            'gimbal_control_unkn1': 1024,
            'gimbal_control_unkn2': 1024,
        },
    )
    print("Sent:", frame.encode().hex())
    transport.close()


if __name__ == '__main__':
    main()

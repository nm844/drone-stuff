"""
DUML v1 protocol enums.

Ground truth confirmed against this project's WM260 firmware disassembly
(see ../../DUML_PROTOCOL/00_FRAME_FORMAT.md and 01_BINARY_ANALYSIS_FINDINGS.md).
"""
from __future__ import annotations
from enum import IntEnum


class DeviceType(IntEnum):
    """5-bit sender/receiver device-type field (frame byte 4 bits0-4, byte 5 bits0-4).

    Confirmed by direct disassembly of the canonical 32-slot name table
    compiled into libduml_frwk.so (duss_parse_host_id/_v2), WM260 (Mavic 3)
    E2 image -- see DUML_PROTOCOL/02_DEVICE_ADDRESSING_EXTENDED.md and
    04_WM260_DAEMON_FINDINGS.md. This confirms every name below by value
    and mostly by semantics, but this firmware generation has renamed
    several slots from the identifiers originally chosen for this enum
    (kept as-is to avoid an API break) -- the firmware's own string for
    each slot is given in the trailing comment where it differs from a
    literal lowercasing of the member name.
    """
    ANY = 0              # firmware string: "whoami" (self-query sentinel in this lookup context)
    CAMERA = 1
    APP = 2              # "mobile"
    FLIGHT_CONTROLLER = 3  # "flight"
    GIMBAL = 4
    CENTER_BOARD = 5     # "cboard"
    REMOTE_CONTROL = 6   # "rc"
    WIFI_AIR = 7         # "network" -- this board has an LTE/4G modem (bin/QFirehose); slot may now be a generic network node rather than specifically wifi-air
    DM36X_AIR = 8        # "ve_air" -- DM36x chip retired this generation; generic video-encoder-air naming
    HD_MCU_AIR = 9       # "vt_air" -- generic video-transmission-air naming
    PC = 10
    BATTERY = 11
    ESC = 12
    DM36X_GROUND = 13    # "ve_gnd"
    HD_MCU_GROUND = 14   # "vt_gnd"
    S2P_USB_AIR = 15     # "s_to_p_air"
    S2P_USB_GROUND = 16  # "s_to_p_gnd"
    MONOCULAR = 17       # "mvision"
    BINOCULAR = 18       # "bvision"
    FPGA_AIR = 19        # "fpga_air"
    FPGA_GROUND = 20     # "fpga_gnd"
    SIMULATOR = 21
    BASE_STATION = 22    # "bstation"
    AIRBORNE_COMPUTING = 23  # "misc"
    RC_BATTERY = 24      # "rcpmu"
    IMU = 25
    GPS_RTK = 26         # "gps"
    WIFI_GROUND = 27     # "wifi_gnd"
    SIG_CVT = 28         # "glass" -- repurposed for DJI FPV Goggles this generation
    PMU = 29             # "blackbox" -- repurposed for the flight-data-recorder service this generation
    UNKNOWN30 = 30       # "test"
    LAST = 31            # "all"


class AckType(IntEnum):
    """2-bit ack-type field (frame byte 8 bits 5-6)."""
    NO_ACK_NEEDED = 0
    ACK_BEFORE_EXEC = 1   # "PUSH"
    ACK_AFTER_EXEC = 2    # acknowledge + return result code


class EncryptType(IntEnum):
    """3-bit encryption-type field (frame byte 8 bits 0-2)."""
    NONE = 0
    AES_128 = 1
    SELF_DEF = 2
    XOR = 3
    DES_56 = 4
    DES_112 = 5
    AES_192 = 6
    AES_256 = 7


class PacketType(IntEnum):
    """1-bit packet-type field (frame byte 8 bit 7)."""
    REQUEST = 0
    RESPONSE = 1


class CmdSet(IntEnum):
    """Command-set selector (frame byte 9). Mostly mirrors DeviceType by
    the usual receiver of that command set, but is its own numbering."""
    GENERAL = 0x00
    SPECIAL = 0x01
    CAMERA = 0x02
    FLIGHT_CONTROL = 0x03
    GIMBAL = 0x04
    CENTER_BOARD = 0x05
    REMOTE_CONTROL = 0x06
    WIFI = 0x07
    DM36X = 0x08
    HD_LINK = 0x09
    MONO_BINOCULAR = 0x0a
    SIMULATOR = 0x0b
    ESC = 0x0c
    BATTERY = 0x0d
    DATA_LOGGER = 0x0e
    RTK = 0x0f
    AUTOMATION = 0x10
    ADSB = 0x11
    # Outside the 0x00-0x11 range documented from the public Wireshark
    # dissector -- found only by static disassembly of a WM260 (Mavic 3)
    # image's daemons/libraries, not from any known capture or prior
    # public dissector source. See DUML_PROTOCOL/04_WM260_DAEMON_FINDINGS.md.
    DEMO_MODE = 0x22
    ROUTE_SWITCH = 0x51


CMD_SET_NAMES = {
    0x00: 'General', 0x01: 'Special', 0x02: 'Camera', 0x03: 'Flight Control',
    0x04: 'Gimbal', 0x05: 'Center Board', 0x06: 'Remote Control', 0x07: 'Wi-Fi',
    0x08: 'DM36x', 0x09: 'HD Link', 0x0a: 'Mono/Binocular (Vision)',
    0x0b: 'Simulator', 0x0c: 'ESC', 0x0d: 'Battery', 0x0e: 'Data Logger',
    0x0f: 'RTK', 0x10: 'Automation', 0x11: 'ADSB',
    0x22: 'Demo Mode', 0x51: 'Route Switch',
}

DEVICE_TYPE_NAMES = {d.value: d.name for d in DeviceType}

# The device type that a cmd_set's commands are typically addressed TO
# (request direction: App/PC/RC -> module). Not enforced by the wire
# format itself (any sender/receiver byte combination is technically
# representable) -- this is a usage convention, included as a convenience
# default for the sender (building requests) and documented, not hard-coded.
CMD_SET_TYPICAL_RECEIVER = {
    0x00: DeviceType.ANY,              # General - varies by target chip
    0x01: DeviceType.FLIGHT_CONTROLLER,
    0x02: DeviceType.CAMERA,
    0x03: DeviceType.FLIGHT_CONTROLLER,
    0x04: DeviceType.GIMBAL,
    0x05: DeviceType.CENTER_BOARD,
    0x06: DeviceType.REMOTE_CONTROL,
    0x07: DeviceType.WIFI_AIR,
    0x08: DeviceType.DM36X_AIR,
    0x09: DeviceType.HD_MCU_AIR,
    0x0a: DeviceType.MONOCULAR,
    0x0b: DeviceType.SIMULATOR,
    0x0c: DeviceType.ESC,
    0x0d: DeviceType.BATTERY,
    0x0e: DeviceType.ANY,
    0x0f: DeviceType.GPS_RTK,
    0x10: DeviceType.ANY,
    0x11: DeviceType.ANY,
    0x22: DeviceType.ANY,  # registered by dji_sys across multiple board variants, not one fixed device role
    0x51: DeviceType.ANY,  # registered as a framework-universal built-in (libduml_frwk.so), like the cmd_set 0x00 built-ins
}

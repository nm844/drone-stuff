# DUML v1 Wire Frame — byte-by-byte

**Status: ground-truth confirmed by disassembly of this exact firmware's `libduml_frwk.so`**
(see `01_BINARY_ANALYSIS_FINDINGS.md` for the disassembly). This is not just the
community/Wireshark-dissector description — every field, bit layout, CRC
algorithm, CRC seed and CRC table byte below was independently verified against
compiled ARM Thumb-2 machine code pulled from `disasm/binding/deps/libduml_frwk.so`
(symbols `CalCrc8`, `CalCrc16`, `DJI_Frame_Cap`, `DjiCrc8Table`), which is part of
the WM260 firmware package itself (`1502_WM260_E1E` aircraft Linux computer, and
also present, byte-identical algorithm, in the `0802_WM260_E2` camera/gimbal
Linux computer). Two independent raw MCU firmware blobs in this exact package
(`0105_LCPU`, `0500_PD_MCU`) also contain the identical CRC8/CRC16 tables,
confirming they speak this same protocol on the wire.

## Overall layout

```
Offset  Size  Field
------  ----  -----------------------------------------------------------
0       1     SOF (Start Of Frame) — always 0x55
1-2     2     ver_length_tag (uint16 LE) — packed length(10 bits) | version(6 bits)
3       1     header_crc8 — CRC8 of bytes[0..2] (SOF + both length bytes)
4       1     sender_info — sender type(bits0-4) | sender index(bits5-7)
5       1     receiver_info — receiver type(bits0-4) | receiver index(bits5-7)
6-7     2     seq_num (uint16 LE) — sequence/retransmission counter
8       1     cmd_type_data — encrypt_type(bits0-2) | ack_type(bits5-6) | packet_type(bit7)
9       1     cmd_set — selects which command table byte 10 is looked up in
10      1     cmd_id — specific command within cmd_set
11..N-3 var   payload (length = whole_length - 11 - 2)
N-2..N-1 2    crc16 (uint16 LE) — CRC16 of bytes[0 .. N-3] (whole frame minus
                                   the CRC16 itself)
```
`N` = `whole_length` = the 10-bit length value decoded from bytes 1-2 (total
frame size including the SOF byte and trailing CRC16).

## Bit-level detail of multi-field bytes

### Bytes 1-2: `ver_length_tag` (uint16, little-endian)
```
 bit:  15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
       |------ version ------|---------- length ---------|
       (6 bits, 0xFC00)        (10 bits, 0x03FF)
```
- `length` = whole frame length in bytes (header + payload + CRC16), max 1023.
- `version` = protocol version; **1** selects the "DUML v1" field layout
  documented here (all fields from byte 4 onward depend on this being 1).
  Firmware ground truth: the Cortex-M/A frame validator rejects (resets its
  state machine) any frame whose computed `length <= 12` — i.e. minimum valid
  frame is 13 bytes (11-byte header + 0-byte payload + 2-byte CRC16).

Disassembly confirms the exact bit split:
```asm
ldrb  r2, [r0, #2]      ; r2 = byte[2]  (high byte)
ldrb  lr, [r0, #1]      ; lr = byte[1]  (low byte)
and   r5, r2, #3        ; r5 = byte[2] & 0x3   <- only bottom 2 bits of byte[2] used
add   r3, lr, r5, lsl #8 ; length = byte[1] | ((byte[2]&3)<<8)   (10-bit value)
```
This is exactly the 0x03FF mask over the little-endian uint16 — the remaining
6 bits of byte[2] (shifted right 2, i.e. `>>10` of the full 16-bit value) are
the version field.

### Byte 3: `header_crc8`
CRC-8 over **bytes [0,1,2]** only (SOF + both length bytes), seed `0x77`,
custom (non-standard) 256-entry table. If the received byte here does not
match the computed value, the frame parser rejects the SOF and resumes
scanning for a new `0x55` (this is literally how it finds frame boundaries in
a continuous stream — the header CRC doubles as frame-sync validation).

Table (`DjiCrc8Table`, confirmed byte-for-byte in `libduml_frwk.so` at file
offset `0xfe800`, and matches `arr_2A103` in `dji-firmware-tools/comm_dat2pcap.py`
exactly):
```
00 5E BC E2 61 3F DD 83 C2 9C 7E 20 A3 FD 1F 41
9D C3 21 7F FC A2 40 1E 5F 01 E3 BD 3E 60 82 DC
23 7D 9F C1 42 1C FE A0 E1 BF 5D 03 80 DE 3C 62
BE E0 02 5C DF 81 63 3D 7C 22 C0 9E 1D 43 A1 FF
46 18 FA A4 27 79 9B C5 84 DA 38 66 E5 BB 59 07
DB 85 67 39 BA E4 06 58 19 47 A5 FB 78 26 C4 9A
65 3B D9 87 04 5A B8 E6 A7 F9 1B 45 C6 98 7A 24
F8 A6 44 1A 99 C7 25 7B 3A 64 86 D8 5B 05 E7 B9
8C D2 30 6E ED B3 51 0F 4E 10 F2 AC 2F 71 93 CD
11 4F AD F3 70 2E CC 92 D3 8D 6F 31 B2 EC 0E 50
AF F1 13 4D CE 90 72 2C 6D 33 D1 8F 0C 52 B0 EE
32 6C 8E D0 53 0D EF B1 F0 AE 4C 12 91 CF 2D 73
CA 94 76 28 AB F5 17 49 08 56 B4 EA 69 37 D5 8B
57 09 EB B5 36 68 8A D4 95 CB 29 77 F4 AA 48 16
E9 B7 55 0B 88 D6 34 6A 2B 75 97 C9 4A 14 F6 A8
74 2A C8 96 15 4B A9 F7 B6 E8 0A 54 D7 89 6B 35
```
Algorithm (confirmed from disassembly, `CalCrc8(seed, data, len)`):
```c
uint8_t CalCrc8(uint8_t seed, const uint8_t *data, int len) {
    for (int i = 0; i < len; i++)
        seed = DjiCrc8Table[seed ^ data[i]];
    return seed;
}
// header_crc8 = CalCrc8(0x77, &frame[0], 3);
```

### Byte 4: `sender_info`
```
bit 7 6 5 | 4 3 2 1 0
    index |  type
```
- `type` (bits 0-4, 0x1F): device type, see table below.
- `index` (bits 5-7, 0xE0): sub-index when multiple devices of the same type
  exist (e.g. dual battery, redundant ESC groups).

### Byte 5: `receiver_info` — identical bit layout to byte 4, for the destination.

### Device type enum (5 bits, values 0-31), shared by sender/receiver:
| # | Device | # | Device | # | Device |
|---|---|---|---|---|---|
| 0 | Invalid/Any | 11 | Battery | 22 | Base Station |
| 1 | Camera (Ambarella) | 12 | ESC | 23 | Airborne computing platform |
| 2 | App | 13 | DM36x transcoder gnd side | 24 | RC battery |
| 3 | Flight Controller | 14 | HD transmission MCU gnd side | 25 | IMU |
| 4 | Gimbal | 15 | Serial-to-parallel (USB) air side | 26 | GPS/RTK |
| 5 | Center Board | 16 | Serial-to-parallel (USB) gnd side | 27 | Wi-Fi gnd side |
| 6 | Remote Control | 17 | Monocular | 28 | Sig_cvt |
| 7 | Wi-Fi air side | 18 | Binocular | 29 | PMU |
| 8 | DM36x transcoder air side | 19 | HD transmission FPGA air side | 30 | Unknown |
| 9 | HD transmission MCU air side | 20 | HD transmission FPGA gnd side | 31 | Last |
| 10 | PC | 21 | Simulator | | |

### Bytes 6-7: `seq_num` (uint16 LE)
Sequence/retransmission counter. If a receiver sees a repeated `seq_num` for
the same (sender, cmd_set, cmd) it treats the request as a retransmit and may
return the previously cached answer rather than re-executing.

### Byte 8: `cmd_type_data`
```
bit:  7      6 5     4 3 2    (bits 3-4 unused/reserved)
     type   ack    encrypt
```
- `packet_type` (bit 7, 0x80): 0 = Request, 1 = Response.
- `ack_type` (bits 5-6, 0x60): 0 = No ACK Needed, 1 = ACK Before Exec ("PUSH"),
  2 = ACK After Exec (acknowledge + return result code).
- `encrypt_type` (bits 0-2, 0x07): 0 = None, 1 = AES-128, 2 = Self-defined,
  3 = XOR, 4 = DES-56, 5 = DES-112, 6 = AES-192, 7 = AES-256.
  (When non-zero, the **payload** bytes [11..N-3] are encrypted under this
  scheme; this reference describes the plaintext/decrypted payload layouts.)

### Byte 9: `cmd_set`
Selects which of the (up to 32) command tables byte 10 is interpreted
against. See `INDEX.md` for the full list with per-set command counts.

### Byte 10: `cmd_id`
The specific command within `cmd_set`. Request and Response packets for the
same logical command normally share the same `cmd_id` and differ only in the
`packet_type` bit and (usually) their payload layout.

### Payload (bytes 11..N-3)
Variable length = `whole_length - 11 - 2`. Structure is command-specific —
see the per-`cmd_set` files in this directory.

### Bytes N-2..N-1: `crc16`
CRC-16/CCITT (reflected, poly 0x1021 bit-reversed = 0x8408), over
**the entire frame except these final 2 bytes** (i.e. bytes `[0 .. N-3]`,
which includes the SOF, header, and payload).

Confirmed seed from disassembly: **`0x3692`**. This literal constant
(`movw r0, #0x3692`) appears right before the `CalCrc16` call in this exact
WM260 firmware's `DJI_Frame_Cap` function — the same seed
`dji-firmware-tools` documents as used by "P3/P4/Mavic" family products,
confirming the WM260 (Mavic-3-class) generation reuses it unchanged. (Other
DJI product families are known to use different seeds — 0x1012 on NAZA-M,
0x1013 on Phantom 2, 0x7000 on NAZA-M V2 — this firmware is definitively in
the 0x3692 family.)

CRC16 table (confirmed byte-for-byte in `libduml_frwk.so` at file offset
`0xd3100`; standard reflected CRC-16/CCITT table):
```
0000 1189 2312 329B 4624 57AD 6536 74BF 8C48 9DC1 AF5A BED3 CA6C DBE5 E97E F8F7
1081 0108 3393 221A 56A5 472C 75B7 643E 9CC9 8D40 BFDB AE52 DAED CB64 F9FF E876
2102 308B 0210 1399 6726 76AF 4434 55BD AD4A BCC3 8E58 9FD1 EB6E FAE7 C87C D9F5
3183 200A 1291 0318 77A7 662E 54B5 453C BDCB AC42 9ED9 8F50 FBEF EA66 D8FD C974
4204 538D 6116 709F 0420 15A9 2732 36BB CE4C DFC5 ED5E FCD7 8868 99E1 AB7A BAF3
5285 430C 7197 601E 14A1 0528 37B3 263A DECD CF44 FDDF EC56 98E9 8960 BBFB AA72
6306 728F 4014 519D 2522 34AB 0630 17B9 EF4E FEC7 CC5C DDD5 A96A B8E3 8A78 9BF1
7387 620E 5095 411C 35A3 242A 16B1 0738 FFCF EE46 DCDD CD54 B9EB A862 9AF9 8B70
8408 9581 A71A B693 C22C D3A5 E13E F0B7 0840 19C9 2B52 3ADB 4E64 5FED 6D76 7CFF
9489 8500 B79B A612 D2AD C324 F1BF E036 18C1 0948 3BD3 2A5A 5EE5 4F6C 7DF7 6C7E
A50A B483 8618 9791 E32E F2A7 C03C D1B5 2942 38CB 0A50 1BD9 6F66 7EEF 4C74 5DFD
B58B A402 9699 8710 F3AF E226 D0BD C134 39C3 284A 1AD1 0B58 7FE7 6E6E 5CF5 4D7C
C60C D785 E51E F497 8028 91A1 A33A B2B3 4A44 5BCD 6956 78DF 0C60 1DE9 2F72 3EFB
D68D C704 F59F E416 90A9 8120 B3BB A232 5AC5 4B4C 79D7 685E 1CE1 0D68 3FF3 2E7A
E70E F687 C41C D595 A12A B0A3 8238 93B1 6B46 7ACF 4854 59DD 2D62 3CEB 0E70 1FF9
F78F E606 D49D C514 B1AB A022 92B9 8330 7BC7 6A4E 58D5 495C 3DE3 2C6A 1EF1 0F78
```
Algorithm (confirmed from disassembly, `CalCrc16(seed, data, len)`):
```c
uint16_t CalCrc16(uint16_t seed, const uint8_t *data, int len) {
    if (len == 0) return 0xFFFF;              // edge case seen in firmware
    for (int i = 0; i < len; i++) {
        uint8_t idx = (uint8_t)(data[i] ^ seed);
        seed = Crc16Table[idx] ^ (seed >> 8);
    }
    return seed;
}
// crc16 = CalCrc16(0x3692, &frame[0], whole_length - 2);
```

## Reference implementation
A complete, runnable Python encoder (ctypes-based, identical bit layout) is
in `dji-firmware-tools/comm_mkdupc.py` (`DJICmdV1Header`/`DJICmdV1Footer`),
and the CRC routines are in `dji-firmware-tools/comm_dat2pcap.py`
(`calc_pkt55_hdr_checksum`, `calc_pkt55_checksum`). Both now independently
confirmed against this firmware's compiled code — see
`01_BINARY_ANALYSIS_FINDINGS.md`.

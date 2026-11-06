// DUML v1 CRC8/CRC16 -- tables and algorithm confirmed by disassembling this
// project's WM260 firmware (libduml_frwk.so: CalCrc8/CalCrc16/DJI_Frame_Cap).
// See ../../DUML_PROTOCOL/00_FRAME_FORMAT.md for the full writeup.
#pragma once
#include <cstdint>
#include <cstddef>

namespace duml {

constexpr uint8_t kCrc8Seed = 0x77;
constexpr uint16_t kCrc16Seed = 0x3692;

extern const uint8_t kCrc8Table[256];
extern const uint16_t kCrc16Table[256];

// CalCrc8(seed, data, len) -- confirmed from firmware disassembly:
//   for each byte: seed = table[seed ^ byte]; return seed;
inline uint8_t Crc8(const uint8_t* data, size_t len, uint8_t seed = kCrc8Seed) {
    uint8_t v = seed;
    for (size_t i = 0; i < len; ++i) {
        v = kCrc8Table[v ^ data[i]];
    }
    return v;
}

// CalCrc16(seed, data, len) -- confirmed from firmware disassembly:
//   if (len == 0) return 0xFFFF;
//   for each byte: idx = byte ^ seed (low 8 bits); seed = table[idx] ^ (seed >> 8);
inline uint16_t Crc16(const uint8_t* data, size_t len, uint16_t seed = kCrc16Seed) {
    if (len == 0) return 0xFFFF;
    uint16_t v = seed;
    for (size_t i = 0; i < len; ++i) {
        uint8_t idx = static_cast<uint8_t>(data[i] ^ v);
        v = static_cast<uint16_t>(kCrc16Table[idx] ^ (v >> 8));
    }
    return v;
}

} // namespace duml

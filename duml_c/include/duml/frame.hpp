// DUML v1 wire-frame codec. Every bit layout and CRC detail here is
// confirmed by disassembling this project's own WM260 firmware
// (libduml_frwk.so). See ../../DUML_PROTOCOL/00_FRAME_FORMAT.md.
//
// Frame layout:
//   0       SOF, always 0x55
//   1-2     length(10 bits) | version(6 bits), uint16 LE
//   3       header_crc8 = CRC8(seed=0x77, bytes[0:3])
//   4       sender_info: type(bits0-4) | index(bits5-7)
//   5       receiver_info: type(bits0-4) | index(bits5-7)
//   6-7     seq_num, uint16 LE
//   8       cmd_type_data: encrypt_type(bits0-2) | ack_type(bits5-6) | packet_type(bit7)
//   9       cmd_set
//   10      cmd_id
//   11..N-3 payload (length = whole_length - 13)
//   N-2..N-1 crc16 = CRC16(seed=0x3692, bytes[0:N-2])
#pragma once
#include <cstdint>
#include <stdexcept>
#include <string>
#include <vector>
#include <optional>

namespace duml {

constexpr uint8_t kSof = 0x55;
constexpr size_t kHeaderLen = 11;
constexpr size_t kCrc16Len = 2;
constexpr size_t kMinFrameLen = kHeaderLen + kCrc16Len; // 13

class FrameError : public std::runtime_error {
public:
    explicit FrameError(const std::string& msg) : std::runtime_error(msg) {}
};

struct Frame {
    uint8_t sender_type = 0;
    uint8_t receiver_type = 0;
    uint8_t cmd_set = 0;
    uint8_t cmd_id = 0;
    std::vector<uint8_t> payload;
    uint8_t sender_index = 0;
    uint8_t receiver_index = 0;
    uint16_t seq_num = 0;
    uint8_t packet_type = 0;   // PacketType
    uint8_t ack_type = 0;      // AckType
    uint8_t encrypt_type = 0;  // EncryptType
    uint8_t version = 1;

    // Encode this frame to wire bytes. Throws FrameError if encrypt_type
    // != kNone (no public key material/algorithm for AES/DES/self-defined
    // encryption is documented for this product -- see README) or if the
    // payload is too long for the 10-bit length field.
    std::vector<uint8_t> Encode() const;

    // Decode exactly one frame from the start of `buf`. Throws FrameError
    // if malformed or (when verify_crc) a CRC mismatch is found. Does not
    // consume/report leftover bytes -- see IterFrames / StreamFramer for
    // continuous streams.
    static Frame Decode(const uint8_t* buf, size_t len, bool verify_crc = true);
    static Frame Decode(const std::vector<uint8_t>& buf, bool verify_crc = true) {
        return Decode(buf.data(), buf.size(), verify_crc);
    }

    size_t WholeLength() const { return kHeaderLen + payload.size() + kCrc16Len; }
};

// Yield every valid Frame found back-to-back starting at buf[0]. Stops at
// the first byte that isn't a valid frame start (does not resynchronize
// mid-buffer -- use StreamFramer in transport.hpp for noisy/live streams).
std::vector<Frame> IterFrames(const uint8_t* buf, size_t len, bool verify_crc = true);

} // namespace duml

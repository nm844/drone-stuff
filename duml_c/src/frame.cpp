#include "duml/frame.hpp"
#include "duml/crc.hpp"
#include "duml/enums.hpp"
#include <cstring>

namespace duml {

namespace {
inline uint16_t ReadU16LE(const uint8_t* p) {
    return static_cast<uint16_t>(p[0] | (p[1] << 8));
}
inline void WriteU16LE(uint8_t* p, uint16_t v) {
    p[0] = static_cast<uint8_t>(v & 0xFF);
    p[1] = static_cast<uint8_t>((v >> 8) & 0xFF);
}
} // namespace

std::vector<uint8_t> Frame::Encode() const {
    if (encrypt_type != static_cast<uint8_t>(EncryptType::kNone)) {
        throw FrameError(
            "encrypt_type != kNone is not supported by this encoder: the wire "
            "format gives no public algorithm/key material for AES/DES/self-"
            "defined -- only XOR(3) is even partially documented upstream and "
            "still needs a per-link key. Construct an already-encrypted "
            "payload yourself and set encrypt_type on the raw bytes you send.");
    }
    if (payload.size() > 0x3FF - kHeaderLen - kCrc16Len) {
        throw FrameError("payload too long for 10-bit length field");
    }

    const size_t whole_length = kHeaderLen + payload.size() + kCrc16Len;
    const uint16_t ver_length_tag = static_cast<uint16_t>(
        (whole_length & 0x03FF) | ((static_cast<uint16_t>(version) & 0x3F) << 10));

    std::vector<uint8_t> out;
    out.reserve(whole_length);
    out.push_back(kSof);
    uint8_t len_bytes[2];
    WriteU16LE(len_bytes, ver_length_tag);
    out.push_back(len_bytes[0]);
    out.push_back(len_bytes[1]);
    out.push_back(0); // placeholder for header_crc8
    out[3] = Crc8(out.data(), 3);

    const uint8_t sender_info = static_cast<uint8_t>((sender_type & 0x1F) | ((sender_index & 0x07) << 5));
    const uint8_t receiver_info = static_cast<uint8_t>((receiver_type & 0x1F) | ((receiver_index & 0x07) << 5));
    out.push_back(sender_info);
    out.push_back(receiver_info);
    uint8_t seq_bytes[2];
    WriteU16LE(seq_bytes, seq_num);
    out.push_back(seq_bytes[0]);
    out.push_back(seq_bytes[1]);

    const uint8_t cmd_type_data = static_cast<uint8_t>(
        (encrypt_type & 0x07) | ((ack_type & 0x03) << 5) | ((packet_type & 0x01) << 7));
    out.push_back(cmd_type_data);
    out.push_back(cmd_set);
    out.push_back(cmd_id);

    // sanity: header must be exactly kHeaderLen bytes so far
    if (out.size() != kHeaderLen) {
        throw FrameError("internal error: header size mismatch");
    }

    out.insert(out.end(), payload.begin(), payload.end());

    const uint16_t fcrc = Crc16(out.data(), out.size());
    uint8_t fcrc_bytes[2];
    WriteU16LE(fcrc_bytes, fcrc);
    out.push_back(fcrc_bytes[0]);
    out.push_back(fcrc_bytes[1]);

    return out;
}

Frame Frame::Decode(const uint8_t* buf, size_t len, bool verify_crc) {
    if (len < kMinFrameLen) {
        throw FrameError("buffer too short");
    }
    if (buf[0] != kSof) {
        throw FrameError("bad SOF byte, expected 0x55");
    }

    const uint16_t ver_length_tag = ReadU16LE(buf + 1);
    const size_t whole_length = ver_length_tag & 0x03FF;
    const uint8_t version = static_cast<uint8_t>((ver_length_tag >> 10) & 0x3F);

    if (whole_length <= 12) {
        throw FrameError("frame length too short (firmware rejects <=12)");
    }
    if (len < whole_length) {
        throw FrameError("buffer shorter than declared frame length");
    }

    if (verify_crc) {
        const uint8_t hcrc = Crc8(buf, 3);
        if (hcrc != buf[3]) {
            throw FrameError("header CRC8 mismatch");
        }
    }
    if (version != 1) {
        throw FrameError("unsupported protocol version (only v1 implemented)");
    }

    const uint8_t sender_info = buf[4];
    const uint8_t receiver_info = buf[5];
    const uint16_t seq_num = ReadU16LE(buf + 6);
    const uint8_t cmd_type_data = buf[8];
    const uint8_t cmd_set = buf[9];
    const uint8_t cmd_id = buf[10];

    if (verify_crc) {
        const uint16_t fcrc = Crc16(buf, whole_length - 2);
        const uint16_t got_fcrc = ReadU16LE(buf + whole_length - 2);
        if (fcrc != got_fcrc) {
            throw FrameError("frame CRC16 mismatch");
        }
    }

    Frame fr;
    fr.sender_type = sender_info & 0x1F;
    fr.sender_index = (sender_info >> 5) & 0x07;
    fr.receiver_type = receiver_info & 0x1F;
    fr.receiver_index = (receiver_info >> 5) & 0x07;
    fr.seq_num = seq_num;
    fr.packet_type = (cmd_type_data >> 7) & 0x01;
    fr.ack_type = (cmd_type_data >> 5) & 0x03;
    fr.encrypt_type = cmd_type_data & 0x07;
    fr.cmd_set = cmd_set;
    fr.cmd_id = cmd_id;
    fr.payload.assign(buf + kHeaderLen, buf + whole_length - 2);
    fr.version = version;
    return fr;
}

std::vector<Frame> IterFrames(const uint8_t* buf, size_t len, bool verify_crc) {
    std::vector<Frame> out;
    size_t offset = 0;
    while (offset < len) {
        try {
            Frame fr = Frame::Decode(buf + offset, len - offset, verify_crc);
            out.push_back(fr);
            offset += fr.WholeLength();
        } catch (const FrameError&) {
            break;
        }
    }
    return out;
}

} // namespace duml

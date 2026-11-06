#include "duml/transport.hpp"
#include "duml/crc.hpp"

namespace duml {

void StreamFramer::ResyncAndParse() {
    size_t i = 0;
    for (;;) {
        // find next candidate SOF
        size_t idx = i;
        while (idx < buf_.size() && buf_[idx] != kSof) ++idx;
        if (idx >= buf_.size()) {
            buf_.clear();
            return;
        }
        if (idx > 0) {
            buf_.erase(buf_.begin(), buf_.begin() + idx);
        }
        if (buf_.size() < kHeaderLen) return; // wait for more header bytes

        uint16_t ver_length_tag = static_cast<uint16_t>(buf_[1] | (buf_[2] << 8));
        size_t length = ver_length_tag & 0x03FF;
        if (length <= 12) {
            buf_.erase(buf_.begin()); // bad length, resync past this SOF byte
            i = 0;
            continue;
        }
        if (verify_crc_ && buf_.size() >= 4) {
            uint8_t hcrc = Crc8(buf_.data(), 3);
            if (hcrc != buf_[3]) {
                buf_.erase(buf_.begin());
                i = 0;
                continue;
            }
        }
        if (buf_.size() < length) return; // wait for the rest of this frame

        try {
            Frame fr = Frame::Decode(buf_.data(), length, verify_crc_);
            ready_.push_back(fr);
            buf_.erase(buf_.begin(), buf_.begin() + length);
            i = 0;
            continue;
        } catch (const FrameError&) {
            buf_.erase(buf_.begin());
            i = 0;
            continue;
        }
    }
}

} // namespace duml

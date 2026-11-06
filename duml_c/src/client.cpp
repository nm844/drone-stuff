#include "duml/client.hpp"
#include "duml/enums.hpp"
#include <cstdio>
#include <thread>

namespace duml {

std::string DecodedFrame::Describe() const {
    char buf[512];
    const char* dir = frame.packet_type ? "RESPONSE" : "REQUEST";
    std::snprintf(buf, sizeof(buf),
                  "<DecodedFrame %s->%s %s/0x%02X '%s' %s seq=%u fields=%zu>",
                  DeviceTypeName(frame.sender_type), DeviceTypeName(frame.receiver_type),
                  spec.CmdSetName(), spec.cmd_id, spec.name, dir,
                  unsigned(frame.seq_num), fields.size());
    return std::string(buf);
}

Frame DumlClient::BuildFrame(uint8_t cmd_set, uint8_t cmd_id, const BuildOptions& opts) {
    CommandSpec spec = RequireCommand(cmd_set, cmd_id);
    Bytes payload;
    if (opts.raw_payload.has_value()) {
        payload = *opts.raw_payload;
    } else if (!spec.fields.empty()) {
        payload = EncodePayload(spec.fields, opts.fields, opts.packet_type, opts.variant);
    } else {
        auto it = opts.fields.find("raw");
        payload = (it != opts.fields.end()) ? GetBytes(opts.fields, "raw") : Bytes();
    }

    Frame fr;
    fr.sender_type = sender_type_;
    fr.sender_index = sender_index_;
    fr.receiver_type = opts.receiver_type;
    fr.receiver_index = opts.receiver_index;
    fr.cmd_set = cmd_set;
    fr.cmd_id = cmd_id;
    fr.payload = std::move(payload);
    fr.packet_type = opts.packet_type;
    fr.ack_type = opts.ack_type;
    fr.seq_num = opts.seq_num.has_value() ? *opts.seq_num : NextSeq();
    return fr;
}

Frame DumlClient::SendFrame(const Frame& frame) {
    auto bytes = frame.Encode();
    transport_.Write(bytes);
    return frame;
}

Frame DumlClient::SendCommand(uint8_t cmd_set, uint8_t cmd_id, const BuildOptions& opts) {
    return SendFrame(BuildFrame(cmd_set, cmd_id, opts));
}

DecodedFrame DumlClient::Wrap(const Frame& frame) {
    CommandSpec spec = RequireCommand(frame.cmd_set, frame.cmd_id);
    FieldMap fields = DecodePayload(spec.fields, frame.payload, frame.packet_type);
    return DecodedFrame{frame, spec, std::move(fields)};
}

DecodedFrame DumlClient::DecodeIncoming(const uint8_t* raw, size_t len) {
    Frame fr = Frame::Decode(raw, len, verify_crc_);
    return Wrap(fr);
}

std::vector<DecodedFrame> DumlClient::Pump(int timeout_ms) {
    auto data = transport_.Read(4096, timeout_ms);
    std::vector<DecodedFrame> out;
    if (!data.empty()) {
        framer_.Feed(data);
        for (auto& fr : framer_.PopReady()) {
            DecodedFrame df = Wrap(fr);
            out.push_back(df);
            auto key = std::make_tuple(fr.cmd_set, fr.cmd_id, fr.seq_num);
            std::lock_guard<std::mutex> lock(pending_mutex_);
            auto it = pending_.find(key);
            if (it != pending_.end()) it->second.push_back(df);
        }
    }
    return out;
}

std::optional<DecodedFrame> DumlClient::SendAndWait(uint8_t cmd_set, uint8_t cmd_id, int timeout_ms,
                                                     BuildOptions opts) {
    if (opts.ack_type == 0) opts.ack_type = 2; // AckType::kAckAfterExec
    Frame frame = BuildFrame(cmd_set, cmd_id, opts);
    auto key = std::make_tuple(cmd_set, cmd_id, frame.seq_num);
    {
        std::lock_guard<std::mutex> lock(pending_mutex_);
        pending_[key] = {};
    }
    SendFrame(frame);

    auto deadline = std::chrono::steady_clock::now() + std::chrono::milliseconds(timeout_ms);
    while (std::chrono::steady_clock::now() < deadline) {
        Pump(50);
        std::lock_guard<std::mutex> lock(pending_mutex_);
        auto it = pending_.find(key);
        if (it != pending_.end() && !it->second.empty()) {
            DecodedFrame result = it->second.front();
            pending_.erase(it);
            return result;
        }
    }
    std::lock_guard<std::mutex> lock(pending_mutex_);
    pending_.erase(key);
    return std::nullopt;
}

void DumlClient::Listen(int duration_ms, const std::function<void(const DecodedFrame&)>& on_frame,
                         int poll_ms) {
    auto deadline = (duration_ms < 0) ? std::chrono::steady_clock::time_point::max()
                                       : std::chrono::steady_clock::now() + std::chrono::milliseconds(duration_ms);
    while (std::chrono::steady_clock::now() < deadline) {
        for (auto& df : Pump(poll_ms)) on_frame(df);
    }
}

std::unique_ptr<FrameListener> DumlClient::StartBackgroundListener(
        std::function<void(const DecodedFrame&)> callback) {
    auto listener = std::make_unique<FrameListener>(
        transport_, [this, callback](const Frame& fr) { callback(Wrap(fr)); }, verify_crc_);
    listener->Start();
    return listener;
}

} // namespace duml

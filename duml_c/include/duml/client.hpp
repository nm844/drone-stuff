// High-level client: build & send a Frame for any (cmd_set, cmd_id) the
// registry knows about (or any raw pair it doesn't -- supply raw payload
// bytes instead of named fields), and decode incoming frames with named
// fields wherever the registry has a known layout.
#pragma once
#include "duml/codecs.hpp"
#include "duml/frame.hpp"
#include "duml/registry.hpp"
#include "duml/transport.hpp"
#include <chrono>
#include <functional>
#include <map>
#include <memory>
#include <mutex>
#include <optional>
#include <string>
#include <tuple>
#include <vector>

namespace duml {

struct DecodedFrame {
    Frame frame;
    CommandSpec spec;
    FieldMap fields;

    std::string Describe() const;
};

// Options for DumlClient::BuildFrame/SendCommand/SendAndWait. A free
// struct (not nested in DumlClient) so its default member initializers
// are fully visible wherever it's used as a default argument.
struct BuildOptions {
    uint8_t receiver_type = 0;         // DeviceType::kAny
    uint8_t receiver_index = 0;
    FieldMap fields;                    // named fields, used if the command has a known layout
    std::optional<Bytes> raw_payload;   // overrides fields entirely if set
    uint8_t packet_type = 0;            // PacketType::kRequest
    uint8_t ack_type = 0;               // AckType::kNoAckNeeded
    std::string variant;                 // branch label substring, for multi-shape commands
    std::optional<uint16_t> seq_num;
};

class DumlClient {
public:
    explicit DumlClient(Transport& transport, uint8_t sender_type = 10 /*PC*/, uint8_t sender_index = 0,
                         bool verify_crc = true)
        : transport_(transport), sender_type_(sender_type), sender_index_(sender_index),
          verify_crc_(verify_crc), framer_(verify_crc) {}

    uint16_t NextSeq() { return static_cast<uint16_t>(++seq_counter_); }

    Frame BuildFrame(uint8_t cmd_set, uint8_t cmd_id, const BuildOptions& opts = {});
    Frame SendFrame(const Frame& frame);
    Frame SendCommand(uint8_t cmd_set, uint8_t cmd_id, const BuildOptions& opts = {});

    // Sends a request (forcing ack_type=kAckAfterExec unless overridden) and
    // blocks until a matching Response (same cmd_set/cmd_id/seq_num) frame
    // is decoded, or `timeout_ms` elapses. Returns std::nullopt on timeout.
    std::optional<DecodedFrame> SendAndWait(uint8_t cmd_set, uint8_t cmd_id, int timeout_ms = 2000,
                                             BuildOptions opts = {});

    DecodedFrame DecodeIncoming(const uint8_t* raw, size_t len);
    DecodedFrame Wrap(const Frame& frame);

    // Pumps the transport for up to `timeout_ms`, returns every frame
    // decoded in that window (possibly empty).
    std::vector<DecodedFrame> Pump(int timeout_ms);

    // Convenience: run Pump() in a loop for `duration_ms` (or forever if
    // negative), calling `on_frame` for each DecodedFrame as it arrives.
    void Listen(int duration_ms, const std::function<void(const DecodedFrame&)>& on_frame,
                int poll_ms = 100);

    // FrameListener holds a non-movable std::atomic, so ownership transfers
    // via unique_ptr; keep it alive for as long as you want the background
    // listener running (its destructor stops the thread).
    std::unique_ptr<FrameListener> StartBackgroundListener(std::function<void(const DecodedFrame&)> callback);

private:
    Transport& transport_;
    uint8_t sender_type_;
    uint8_t sender_index_;
    bool verify_crc_;
    uint32_t seq_counter_ = 0;
    StreamFramer framer_;
    std::mutex pending_mutex_;
    std::map<std::tuple<uint8_t, uint8_t, uint16_t>, std::vector<DecodedFrame>> pending_;
};

} // namespace duml

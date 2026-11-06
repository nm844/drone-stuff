// Transport abstraction + byte-stream framer.
//
// A Transport just moves raw bytes in both directions; StreamFramer does
// the work of finding valid DUML frames inside a possibly-noisy,
// possibly-fragmented byte stream -- the same resynchronization approach
// as the firmware's own DJI_Frame_Cap: scan for 0x55, validate header
// CRC8 before trusting the length field, validate CRC16 before accepting
// the frame.
#pragma once
#include "duml/frame.hpp"
#include <atomic>
#include <cstdint>
#include <functional>
#include <memory>
#include <string>
#include <thread>
#include <vector>

namespace duml {

class Transport {
public:
    virtual ~Transport() = default;
    virtual void Write(const uint8_t* data, size_t len) = 0;
    void Write(const std::vector<uint8_t>& data) { Write(data.data(), data.size()); }

    // Returns whatever bytes are available within `timeout_ms` (may return
    // an empty vector on timeout -- must not block forever). timeout_ms < 0
    // means block until at least one byte arrives (or the transport closes).
    virtual std::vector<uint8_t> Read(size_t max_bytes = 4096, int timeout_ms = 200) = 0;

    virtual void Close() {}
};

class StreamFramer {
public:
    explicit StreamFramer(bool verify_crc = true) : verify_crc_(verify_crc) {}

    void Feed(const uint8_t* data, size_t len) {
        buf_.insert(buf_.end(), data, data + len);
        ResyncAndParse();
    }
    void Feed(const std::vector<uint8_t>& data) { Feed(data.data(), data.size()); }

    std::vector<Frame> PopReady() {
        std::vector<Frame> out;
        out.swap(ready_);
        return out;
    }

private:
    void ResyncAndParse();

    std::vector<uint8_t> buf_;
    std::vector<Frame> ready_;
    bool verify_crc_;
};

// Runs a background thread reading from a Transport, feeding a
// StreamFramer, and calling `callback(frame)` for every decoded frame.
class FrameListener {
public:
    FrameListener(Transport& transport, std::function<void(const Frame&)> callback,
                  bool verify_crc = true, int poll_timeout_ms = 200)
        : transport_(transport), callback_(std::move(callback)),
          framer_(verify_crc), poll_timeout_ms_(poll_timeout_ms) {}
    ~FrameListener() { Stop(); }

    void Start() {
        stop_.store(false);
        thread_ = std::thread([this] { Run(); });
    }
    void Stop() {
        stop_.store(true);
        if (thread_.joinable()) thread_.join();
    }

private:
    void Run() {
        while (!stop_.load()) {
            auto data = transport_.Read(4096, poll_timeout_ms_);
            if (!data.empty()) {
                framer_.Feed(data);
                for (auto& fr : framer_.PopReady()) {
                    try { callback_(fr); } catch (...) {}
                }
            }
        }
    }

    Transport& transport_;
    std::function<void(const Frame&)> callback_;
    StreamFramer framer_;
    int poll_timeout_ms_;
    std::atomic<bool> stop_{false};
    std::thread thread_;
};

// --- Concrete transports -------------------------------------------------

// POSIX serial port (termios). Works on macOS/Linux. For Windows, swap in
// an equivalent implementation using the Win32 Serial Communications API.
class SerialTransport : public Transport {
public:
    explicit SerialTransport(const std::string& port, int baud = 115200);
    ~SerialTransport() override;
    void Write(const uint8_t* data, size_t len) override;
    std::vector<uint8_t> Read(size_t max_bytes, int timeout_ms) override;
    void Close() override;

private:
    int fd_ = -1;
};

// POSIX TCP client/server, for DUML-over-network bridges (e.g. a USB-bulk
// <-> TCP proxy, or testing against a recorded/replayed stream).
class TcpTransport : public Transport {
public:
    TcpTransport(const std::string& host, int port, int connect_timeout_ms = 5000);
    ~TcpTransport() override;
    void Write(const uint8_t* data, size_t len) override;
    std::vector<uint8_t> Read(size_t max_bytes, int timeout_ms) override;
    void Close() override;

private:
    int fd_ = -1;
};

class TcpServerTransport : public Transport {
public:
    // Listens and accepts exactly one inbound connection.
    TcpServerTransport(const std::string& host, int port, int accept_timeout_ms = 30000);
    ~TcpServerTransport() override;
    void Write(const uint8_t* data, size_t len) override;
    std::vector<uint8_t> Read(size_t max_bytes, int timeout_ms) override;
    void Close() override;

private:
    int fd_ = -1;
};

} // namespace duml

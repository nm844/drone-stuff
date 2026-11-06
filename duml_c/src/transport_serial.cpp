// POSIX serial transport (macOS/Linux). Not compiled on Windows -- see
// Makefile's DUML_NO_SERIAL guard for platforms without termios.
#include "duml/transport.hpp"
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <poll.h>
#include <stdexcept>
#include <termios.h>
#include <unistd.h>

namespace duml {

namespace {
speed_t BaudToSpeed(int baud) {
    switch (baud) {
        case 9600: return B9600;
        case 19200: return B19200;
        case 38400: return B38400;
        case 57600: return B57600;
        case 115200: return B115200;
        case 230400: return B230400;
#ifdef B460800
        case 460800: return B460800;
#endif
#ifdef B921600
        case 921600: return B921600;
#endif
        default: return B115200;
    }
}
} // namespace

SerialTransport::SerialTransport(const std::string& port, int baud) {
    fd_ = ::open(port.c_str(), O_RDWR | O_NOCTTY | O_NONBLOCK);
    if (fd_ < 0) {
        throw std::runtime_error("SerialTransport: open(" + port + ") failed: " + std::strerror(errno));
    }
    termios tty{};
    if (tcgetattr(fd_, &tty) != 0) {
        ::close(fd_);
        throw std::runtime_error(std::string("SerialTransport: tcgetattr failed: ") + std::strerror(errno));
    }
    cfsetospeed(&tty, BaudToSpeed(baud));
    cfsetispeed(&tty, BaudToSpeed(baud));
    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8; // 8 data bits
    tty.c_cflag &= ~PARENB;                      // no parity
    tty.c_cflag &= ~CSTOPB;                      // 1 stop bit
    tty.c_cflag &= ~CRTSCTS;                     // no hw flow control
    tty.c_cflag |= CREAD | CLOCAL;
    tty.c_lflag = 0;   // raw: no canonical mode, no echo, no signals
    tty.c_iflag &= ~(IXON | IXOFF | IXANY);
    tty.c_iflag &= ~(ICRNL | INLCR | IGNCR);
    tty.c_oflag = 0;
    tty.c_cc[VMIN] = 0;
    tty.c_cc[VTIME] = 0;
    if (tcsetattr(fd_, TCSANOW, &tty) != 0) {
        ::close(fd_);
        throw std::runtime_error(std::string("SerialTransport: tcsetattr failed: ") + std::strerror(errno));
    }
}

SerialTransport::~SerialTransport() { Close(); }

void SerialTransport::Close() {
    if (fd_ >= 0) {
        ::close(fd_);
        fd_ = -1;
    }
}

void SerialTransport::Write(const uint8_t* data, size_t len) {
    size_t written = 0;
    while (written < len) {
        ssize_t n = ::write(fd_, data + written, len - written);
        if (n < 0) {
            if (errno == EAGAIN || errno == EINTR) continue;
            throw std::runtime_error(std::string("SerialTransport::Write failed: ") + std::strerror(errno));
        }
        written += static_cast<size_t>(n);
    }
}

std::vector<uint8_t> SerialTransport::Read(size_t max_bytes, int timeout_ms) {
    pollfd pfd{fd_, POLLIN, 0};
    int rc = ::poll(&pfd, 1, timeout_ms);
    if (rc <= 0) return {};
    std::vector<uint8_t> buf(max_bytes);
    ssize_t n = ::read(fd_, buf.data(), max_bytes);
    if (n <= 0) return {};
    buf.resize(static_cast<size_t>(n));
    return buf;
}

} // namespace duml

// POSIX socket transport.
#include "duml/transport.hpp"
#include <arpa/inet.h>
#include <cerrno>
#include <cstring>
#include <fcntl.h>
#include <netdb.h>
#include <poll.h>
#include <stdexcept>
#include <sys/socket.h>
#include <unistd.h>

namespace duml {

namespace {
void SetNonBlocking(int fd) {
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);
}
} // namespace

TcpTransport::TcpTransport(const std::string& host, int port, int connect_timeout_ms) {
    addrinfo hints{};
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    addrinfo* res = nullptr;
    std::string port_str = std::to_string(port);
    int gai = getaddrinfo(host.c_str(), port_str.c_str(), &hints, &res);
    if (gai != 0) {
        throw std::runtime_error(std::string("TcpTransport: getaddrinfo failed: ") + gai_strerror(gai));
    }
    fd_ = -1;
    for (addrinfo* p = res; p != nullptr; p = p->ai_next) {
        fd_ = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (fd_ < 0) continue;
        SetNonBlocking(fd_);
        int rc = connect(fd_, p->ai_addr, p->ai_addrlen);
        if (rc == 0) break;
        if (errno == EINPROGRESS) {
            pollfd pfd{fd_, POLLOUT, 0};
            rc = poll(&pfd, 1, connect_timeout_ms);
            if (rc > 0 && (pfd.revents & POLLOUT)) {
                int err = 0; socklen_t len = sizeof(err);
                getsockopt(fd_, SOL_SOCKET, SO_ERROR, &err, &len);
                if (err == 0) break;
            }
        }
        ::close(fd_);
        fd_ = -1;
    }
    freeaddrinfo(res);
    if (fd_ < 0) {
        throw std::runtime_error("TcpTransport: could not connect to " + host + ":" + port_str);
    }
}

TcpTransport::~TcpTransport() { Close(); }
void TcpTransport::Close() { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }

void TcpTransport::Write(const uint8_t* data, size_t len) {
    size_t written = 0;
    while (written < len) {
        ssize_t n = ::send(fd_, data + written, len - written, 0);
        if (n < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
            throw std::runtime_error(std::string("TcpTransport::Write failed: ") + std::strerror(errno));
        }
        written += static_cast<size_t>(n);
    }
}

std::vector<uint8_t> TcpTransport::Read(size_t max_bytes, int timeout_ms) {
    pollfd pfd{fd_, POLLIN, 0};
    int rc = ::poll(&pfd, 1, timeout_ms);
    if (rc <= 0) return {};
    std::vector<uint8_t> buf(max_bytes);
    ssize_t n = ::recv(fd_, buf.data(), max_bytes, 0);
    if (n <= 0) return {};
    buf.resize(static_cast<size_t>(n));
    return buf;
}

// --- Server side ----------------------------------------------------------

TcpServerTransport::TcpServerTransport(const std::string& host, int port, int accept_timeout_ms) {
    int srv = socket(AF_INET, SOCK_STREAM, 0);
    if (srv < 0) throw std::runtime_error("TcpServerTransport: socket() failed");
    int opt = 1;
    setsockopt(srv, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt));

    sockaddr_in addr{};
    addr.sin_family = AF_INET;
    addr.sin_port = htons(static_cast<uint16_t>(port));
    if (host.empty() || host == "0.0.0.0") {
        addr.sin_addr.s_addr = INADDR_ANY;
    } else {
        inet_pton(AF_INET, host.c_str(), &addr.sin_addr);
    }
    if (bind(srv, reinterpret_cast<sockaddr*>(&addr), sizeof(addr)) != 0) {
        ::close(srv);
        throw std::runtime_error(std::string("TcpServerTransport: bind failed: ") + std::strerror(errno));
    }
    if (listen(srv, 1) != 0) {
        ::close(srv);
        throw std::runtime_error("TcpServerTransport: listen failed");
    }
    pollfd pfd{srv, POLLIN, 0};
    int rc = poll(&pfd, 1, accept_timeout_ms);
    if (rc <= 0) {
        ::close(srv);
        throw std::runtime_error("TcpServerTransport: accept timed out");
    }
    fd_ = accept(srv, nullptr, nullptr);
    ::close(srv);
    if (fd_ < 0) {
        throw std::runtime_error("TcpServerTransport: accept failed");
    }
    SetNonBlocking(fd_);
}

TcpServerTransport::~TcpServerTransport() { Close(); }
void TcpServerTransport::Close() { if (fd_ >= 0) { ::close(fd_); fd_ = -1; } }

void TcpServerTransport::Write(const uint8_t* data, size_t len) {
    size_t written = 0;
    while (written < len) {
        ssize_t n = ::send(fd_, data + written, len - written, 0);
        if (n < 0) {
            if (errno == EAGAIN || errno == EWOULDBLOCK || errno == EINTR) continue;
            throw std::runtime_error(std::string("TcpServerTransport::Write failed: ") + std::strerror(errno));
        }
        written += static_cast<size_t>(n);
    }
}

std::vector<uint8_t> TcpServerTransport::Read(size_t max_bytes, int timeout_ms) {
    pollfd pfd{fd_, POLLIN, 0};
    int rc = ::poll(&pfd, 1, timeout_ms);
    if (rc <= 0) return {};
    std::vector<uint8_t> buf(max_bytes);
    ssize_t n = ::recv(fd_, buf.data(), max_bytes, 0);
    if (n <= 0) return {};
    buf.resize(static_cast<size_t>(n));
    return buf;
}

} // namespace duml

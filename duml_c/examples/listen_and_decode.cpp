// Print every decoded DUML frame from a serial port or TCP endpoint.
//   ./listen_and_decode serial /dev/ttyUSB0
//   ./listen_and_decode tcp 127.0.0.1 9000
#include "duml/client.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <memory>
using namespace duml;

int main(int argc, char** argv) {
    std::unique_ptr<Transport> t;
    if (argc >= 3 && !std::strcmp(argv[1], "serial")) t = std::make_unique<SerialTransport>(argv[2], 115200);
    else if (argc >= 4 && !std::strcmp(argv[1], "tcp")) t = std::make_unique<TcpTransport>(argv[2], std::atoi(argv[3]));
    else { std::fprintf(stderr, "usage: %s serial DEV | tcp HOST PORT\n", argv[0]); return 2; }
    DumlClient client(*t);
    client.Listen(-1, [](const DecodedFrame& df) { std::printf("%s\n", df.Describe().c_str()); });
    return 0;
}

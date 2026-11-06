// Send a Gimbal Control command over serial: ./send_gimbal_control /dev/ttyUSB0
#include "duml/client.hpp"
#include "duml/commands.hpp"
#include "duml/enums.hpp"
#include <cstdio>
using namespace duml;

int main(int argc, char** argv) {
    if (argc < 2) { std::fprintf(stderr, "usage: %s <serial-port>\n", argv[0]); return 2; }
    SerialTransport transport(argv[1], 115200);
    DumlClient client(transport, static_cast<uint8_t>(DeviceType::kApp));

    BuildOptions opts;
    opts.receiver_type = static_cast<uint8_t>(DeviceType::kGimbal);
    opts.fields["gimbal_control_unkn0"] = Value(int64_t(1024));  // mid-scale of the 363..1685 range
    opts.fields["gimbal_control_unkn1"] = Value(int64_t(1024));
    opts.fields["gimbal_control_unkn2"] = Value(int64_t(1024));
    Frame sent = client.SendCommand(cmd::gimbal::kCmdSet, cmd::gimbal::kGimbalControl, opts);
    std::printf("sent seq=%u\n", sent.seq_num);
    return 0;
}

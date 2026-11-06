// duml_cli -- command-line tool for the duml C++ library.
//
//   duml_cli list [--cmd-set N]
//   duml_cli show --cmd-set N --cmd-id N
//   duml_cli decode HEX...
//   duml_cli send --transport serial|tcp --port DEV|N [--host H] [--baud B]
//                 --cmd-set N --cmd-id N [--receiver-type N] [--field k=v]...
//                 [--raw HEX] [--ack N] [--wait]
//   duml_cli listen --transport serial|tcp --port DEV|N [--host H] [--duration-ms N]
#include "duml/client.hpp"
#include "duml/enums.hpp"
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <iostream>
#include <memory>
#include <sstream>
#include <string>
#include <vector>

using namespace duml;

namespace {

int ParseInt(const std::string& s) { return static_cast<int>(std::strtol(s.c_str(), nullptr, 0)); }

Bytes ParseHex(const std::string& s) {
    Bytes out;
    std::string clean;
    for (char c : s) if (std::isxdigit(static_cast<unsigned char>(c))) clean.push_back(c);
    for (size_t i = 0; i + 1 < clean.size(); i += 2) {
        out.push_back(static_cast<uint8_t>(std::stoul(clean.substr(i, 2), nullptr, 16)));
    }
    return out;
}

std::string HexStr(const Bytes& b) {
    std::string out;
    char buf[4];
    for (auto x : b) { std::snprintf(buf, sizeof(buf), "%02x", x); out += buf; }
    return out;
}

void PrintValue(const Value& v) {
    if (auto p = std::get_if<int64_t>(&v)) std::printf("%lld", (long long)*p);
    else if (auto p = std::get_if<double>(&v)) std::printf("%g", *p);
    else if (auto p = std::get_if<Bytes>(&v)) std::printf("bytes(%s)", HexStr(*p).c_str());
    else if (auto p = std::get_if<std::string>(&v)) std::printf("\"%s\"", p->c_str());
}

int CmdList(int argc, char** argv) {
    int want_set = -1;
    for (int i = 0; i < argc; ++i)
        if (!std::strcmp(argv[i], "--cmd-set") && i + 1 < argc) want_set = ParseInt(argv[++i]);
    for (const auto& s : AllCommands()) {
        if (want_set >= 0 && s.cmd_set != want_set) continue;
        std::printf("0x%02X/0x%02X  [%s]  %-24s %s\n", s.cmd_set, s.cmd_id,
                    std::string(s.decode_status) == "full" ? "FULL " : "none ", s.CmdSetName(), s.name);
    }
    return 0;
}

int CmdShow(int argc, char** argv) {
    int cs = -1, ci = -1;
    for (int i = 0; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--cmd-set") && i + 1 < argc) cs = ParseInt(argv[++i]);
        else if (!std::strcmp(argv[i], "--cmd-id") && i + 1 < argc) ci = ParseInt(argv[++i]);
    }
    if (cs < 0 || ci < 0) { std::fprintf(stderr, "show requires --cmd-set and --cmd-id\n"); return 2; }
    const CommandSpec* spec = LookupCommand(static_cast<uint8_t>(cs), static_cast<uint8_t>(ci));
    if (!spec) { std::printf("No registry entry (still sendable/receivable as raw bytes).\n"); return 0; }
    std::printf("%s\n", spec->Describe().c_str());
    if (spec->note[0]) std::printf("Note: %s\n", spec->note);
    if (spec->fields.empty()) { std::printf("  (no known byte-level payload structure -- raw bytes only)\n"); return 0; }
    for (size_t i = 0; i < spec->fields.count; ++i) {
        const Field& f = spec->fields.fields[i];
        std::printf("  off=%3d size=%3d %-8s %s", f.offset, f.size, f.type, f.name);
        if (f.mask) std::printf(" mask=0x%X", f.mask);
        if (f.branch[0]) std::printf(" [%s]", f.branch);
        if (f.desc[0]) std::printf(" -- %s", f.desc);
        std::printf("\n");
    }
    return 0;
}

int CmdDecode(int argc, char** argv) {
    std::string joined;
    for (int i = 0; i < argc; ++i) joined += argv[i];
    Bytes raw = ParseHex(joined);
    Frame fr = Frame::Decode(raw);
    CommandSpec spec = RequireCommand(fr.cmd_set, fr.cmd_id);
    FieldMap fields = DecodePayload(spec.fields, fr.payload, fr.packet_type);
    std::printf("Sender:   %s (index %u)\n", DeviceTypeName(fr.sender_type), fr.sender_index);
    std::printf("Receiver: %s (index %u)\n", DeviceTypeName(fr.receiver_type), fr.receiver_index);
    std::printf("Cmd Set:  0x%02X (%s)\n", fr.cmd_set, spec.CmdSetName());
    std::printf("Cmd Id:   0x%02X (%s)\n", fr.cmd_id, spec.name);
    std::printf("Seq:      %u\n", fr.seq_num);
    std::printf("Type:     %s  Ack=%u  Encrypt=%u\n", fr.packet_type ? "RESPONSE" : "REQUEST", fr.ack_type, fr.encrypt_type);
    std::printf("Payload:  %s (%zu bytes)\n", HexStr(fr.payload).c_str(), fr.payload.size());
    if (std::string(spec.decode_status) == "full") {
        std::printf("Decoded fields:\n");
        for (const auto& [k, v] : fields) { std::printf("  %s = ", k.c_str()); PrintValue(v); std::printf("\n"); }
    } else {
        std::printf("  (payload structure unknown -- shown as raw bytes above)\n");
    }
    return 0;
}

struct TransportArgs {
    std::string kind, host = "127.0.0.1", port_str;
    int baud = 115200;
};

std::unique_ptr<Transport> MakeTransport(const TransportArgs& a) {
    if (a.kind == "serial") return std::make_unique<SerialTransport>(a.port_str, a.baud);
    if (a.kind == "tcp") return std::make_unique<TcpTransport>(a.host, ParseInt(a.port_str));
    if (a.kind == "tcp-server") return std::make_unique<TcpServerTransport>(a.host, ParseInt(a.port_str));
    throw std::runtime_error("unknown --transport (use serial|tcp|tcp-server)");
}

int CmdSend(int argc, char** argv) {
    TransportArgs ta;
    int cs = -1, ci = -1, recv = 0, ack = 0;
    std::string raw_hex;
    bool wait = false;
    std::vector<std::string> field_args;
    for (int i = 0; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() { return std::string(argv[++i]); };
        if (a == "--transport") ta.kind = next();
        else if (a == "--port") ta.port_str = next();
        else if (a == "--host") ta.host = next();
        else if (a == "--baud") ta.baud = ParseInt(next());
        else if (a == "--cmd-set") cs = ParseInt(next());
        else if (a == "--cmd-id") ci = ParseInt(next());
        else if (a == "--receiver-type") recv = ParseInt(next());
        else if (a == "--ack") ack = ParseInt(next());
        else if (a == "--raw") raw_hex = next();
        else if (a == "--field") field_args.push_back(next());
        else if (a == "--wait") wait = true;
    }
    if (cs < 0 || ci < 0) { std::fprintf(stderr, "send requires --cmd-set and --cmd-id\n"); return 2; }
    auto transport = MakeTransport(ta);
    DumlClient client(*transport);
    BuildOptions opts;
    opts.receiver_type = static_cast<uint8_t>(recv);
    opts.ack_type = static_cast<uint8_t>(ack);
    for (const auto& fa : field_args) {
        auto eq = fa.find('=');
        if (eq == std::string::npos) continue;
        opts.fields[fa.substr(0, eq)] = Value(static_cast<int64_t>(std::strtoll(fa.c_str() + eq + 1, nullptr, 0)));
    }
    if (!raw_hex.empty()) opts.raw_payload = ParseHex(raw_hex);

    Frame fr = client.BuildFrame(static_cast<uint8_t>(cs), static_cast<uint8_t>(ci), opts);
    std::printf("Sending: %s\n", HexStr(fr.Encode()).c_str());
    client.SendFrame(fr);
    if (wait) {
        auto resp = client.SendAndWait(static_cast<uint8_t>(cs), static_cast<uint8_t>(ci), 2000, opts);
        std::printf("Response: %s\n", resp ? resp->Describe().c_str() : "(timeout)");
    }
    return 0;
}

int CmdListen(int argc, char** argv) {
    TransportArgs ta;
    int duration_ms = -1;
    for (int i = 0; i < argc; ++i) {
        std::string a = argv[i];
        auto next = [&]() { return std::string(argv[++i]); };
        if (a == "--transport") ta.kind = next();
        else if (a == "--port") ta.port_str = next();
        else if (a == "--host") ta.host = next();
        else if (a == "--baud") ta.baud = ParseInt(next());
        else if (a == "--duration-ms") duration_ms = ParseInt(next());
    }
    auto transport = MakeTransport(ta);
    DumlClient client(*transport);
    client.Listen(duration_ms, [](const DecodedFrame& df) {
        std::printf("%s\n", df.Describe().c_str());
        for (const auto& [k, v] : df.fields) { std::printf("  %s = ", k.c_str()); PrintValue(v); std::printf("\n"); }
    });
    return 0;
}

void Usage() {
    std::fprintf(stderr,
        "usage: duml_cli <list|show|decode|send|listen> [options]\n"
        "  list   [--cmd-set N]\n"
        "  show   --cmd-set N --cmd-id N\n"
        "  decode HEXBYTES...\n"
        "  send   --transport serial|tcp --port DEV|N [--host H] [--baud B] --cmd-set N --cmd-id N\n"
        "         [--receiver-type N] [--field name=value]... [--raw HEX] [--ack N] [--wait]\n"
        "  listen --transport serial|tcp --port DEV|N [--host H] [--baud B] [--duration-ms N]\n");
}

} // namespace

int main(int argc, char** argv) {
    if (argc < 2) { Usage(); return 2; }
    std::string cmd = argv[1];
    try {
        if (cmd == "list") return CmdList(argc - 2, argv + 2);
        if (cmd == "show") return CmdShow(argc - 2, argv + 2);
        if (cmd == "decode") return CmdDecode(argc - 2, argv + 2);
        if (cmd == "send") return CmdSend(argc - 2, argv + 2);
        if (cmd == "listen") return CmdListen(argc - 2, argv + 2);
    } catch (const std::exception& e) {
        std::fprintf(stderr, "Error: %s\n", e.what());
        return 1;
    }
    Usage();
    return 2;
}

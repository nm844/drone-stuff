#include "duml/registry.hpp"
#include "duml/enums.hpp"
#include <algorithm>
#include <cstdio>

namespace duml {

// Defined in generated/registry_data.cpp
extern const CommandSpec kCommandTable[];
extern const size_t kCommandTableSize;

const char* CommandSpec::CmdSetName() const { return duml::CmdSetName(cmd_set); }

std::string CommandSpec::Describe() const {
    char buf[256];
    std::snprintf(buf, sizeof(buf), "<CommandSpec %s/0x%02X '%s' decode=%s>",
                  CmdSetName(), cmd_id, name, decode_status);
    return std::string(buf);
}

const CommandSpec* LookupCommand(uint8_t cmd_set, uint8_t cmd_id) {
    for (size_t i = 0; i < kCommandTableSize; ++i) {
        if (kCommandTable[i].cmd_set == cmd_set && kCommandTable[i].cmd_id == cmd_id) {
            return &kCommandTable[i];
        }
    }
    return nullptr;
}

CommandSpec RequireCommand(uint8_t cmd_set, uint8_t cmd_id) {
    const CommandSpec* found = LookupCommand(cmd_set, cmd_id);
    if (found) return *found;
    static char name_buf[64];
    std::snprintf(name_buf, sizeof(name_buf), "Unregistered_0x%02X", cmd_id);
    CommandSpec stub{};
    stub.cmd_set = cmd_set;
    stub.cmd_id = cmd_id;
    stub.name = name_buf;
    stub.decode_status = "none";
    stub.fields = FieldSpan{nullptr, 0};
    stub.source = "";
    stub.dissector_fn = "";
    stub.note = "";
    return stub;
}

const std::vector<CommandSpec>& AllCommands() {
    static const std::vector<CommandSpec> all(kCommandTable, kCommandTable + kCommandTableSize);
    return all;
}

std::vector<const CommandSpec*> CommandsInSet(uint8_t cmd_set) {
    std::vector<const CommandSpec*> out;
    for (size_t i = 0; i < kCommandTableSize; ++i) {
        if (kCommandTable[i].cmd_set == cmd_set) out.push_back(&kCommandTable[i]);
    }
    std::sort(out.begin(), out.end(), [](const CommandSpec* a, const CommandSpec* b) {
        return a->cmd_id < b->cmd_id;
    });
    return out;
}

namespace {
std::string Lower(const std::string& s) {
    std::string out = s;
    std::transform(out.begin(), out.end(), out.begin(), [](unsigned char c) { return std::tolower(c); });
    return out;
}
} // namespace

std::vector<const CommandSpec*> FindByName(const std::string& needle) {
    std::string lneedle = Lower(needle);
    std::vector<const CommandSpec*> out;
    for (size_t i = 0; i < kCommandTableSize; ++i) {
        if (Lower(kCommandTable[i].name).find(lneedle) != std::string::npos) {
            out.push_back(&kCommandTable[i]);
        }
    }
    return out;
}

RegistryStats GetRegistryStats() {
    RegistryStats s{kCommandTableSize, 0, 0};
    for (size_t i = 0; i < kCommandTableSize; ++i) {
        if (std::string(kCommandTable[i].decode_status) == "full") ++s.full;
        else ++s.none;
    }
    return s;
}

} // namespace duml

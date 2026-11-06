// Command registry: static data generated from duml_py/duml/commands.json
// (itself generated from the Wireshark dissector source -- see
// ../../DUML_PROTOCOL/README.md). Covers every (cmd_set, cmd_id) pair known
// from the public dji-firmware-tools dissector. `decode_status` is "full"
// only where the payload byte layout is actually known; everything else
// still looks up by name/id and is sendable/receivable as raw bytes via
// codecs.hpp with an empty FieldSpan.
#pragma once
#include "duml/codecs.hpp"
#include <cstdint>
#include <string>
#include <vector>

namespace duml {

struct CommandSpec {
    uint8_t cmd_set;
    uint8_t cmd_id;
    const char* name;            // never null
    const char* decode_status;    // "full" or "none"
    FieldSpan fields;              // empty if decode_status == "none"
    const char* source;           // never null (may be "")
    const char* dissector_fn;     // never null (may be "")
    const char* note;              // never null (may be "")

    const char* CmdSetName() const;
    std::string Describe() const;
};

// Returns nullptr if (cmd_set, cmd_id) isn't registered.
const CommandSpec* LookupCommand(uint8_t cmd_set, uint8_t cmd_id);

// Always returns a valid pointer: a synthesized stub (decode_status="none",
// empty fields, name "Unregistered_0xXX") if the pair isn't registered, so
// callers never need to special-case "totally unknown command".
CommandSpec RequireCommand(uint8_t cmd_set, uint8_t cmd_id);

// All registered commands, cmd_set-major, cmd_id-minor order.
const std::vector<CommandSpec>& AllCommands();

std::vector<const CommandSpec*> CommandsInSet(uint8_t cmd_set);

// Case-insensitive substring search over command names.
std::vector<const CommandSpec*> FindByName(const std::string& needle);

struct RegistryStats { size_t total; size_t full; size_t none; };
RegistryStats GetRegistryStats();

} // namespace duml

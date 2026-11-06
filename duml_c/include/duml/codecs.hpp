// Payload field codec: turns a command's field spec (same data the Python
// duml_py/duml/codecs.py works from -- see ../../DUML_PROTOCOL/README.md
// for how that spec was derived from the Wireshark dissector source) into
// actual encode()/decode() of payload bytes.
//
// Fields sharing the same `offset` are bitfield siblings of one underlying
// integer and are combined/split via each field's `mask`. Fields tagged
// with a `branch` (an "if pack_type == 0 then" or "if (payload:len() >= N)
// then" condition, verbatim from the source dissector) are grouped into
// alternative/optional field sets; see SelectBranch().
#pragma once
#include <cstdint>
#include <map>
#include <optional>
#include <stdexcept>
#include <string>
#include <variant>
#include <vector>

namespace duml {

using Bytes = std::vector<uint8_t>;

// A decoded/to-be-encoded field value. Integers (signed or unsigned, any
// width) go in kInt; floats/doubles in kDouble; raw byte blobs and
// fixed-size strings in kBytes/kString.
using Value = std::variant<int64_t, double, Bytes, std::string>;
using FieldMap = std::map<std::string, Value>;

class CodecError : public std::runtime_error {
public:
    explicit CodecError(const std::string& msg) : std::runtime_error(msg) {}
};

// One payload field, as generated from the dissector source. Pointers are
// into static string literal data (see generated/registry_data.cpp) and
// are never null except where noted.
struct Field {
    const char* name;         // never null
    const char* label;        // never null (may be "")
    int offset;                // byte offset within payload
    int size;                  // byte size (0 if genuinely variable-length, rare)
    const char* type;         // "uint8".."uint64","int8".."int64","float","double","bytes","string","ether"
    const char* enum_name;     // never null (may be "") -- name of the source enum table, informational only
    uint32_t mask;             // 0 if this field is not a bitfield slice
    const char* desc;         // never null (may be "")
    const char* branch;       // never null (may be "") -- verbatim branch condition text
};

struct FieldSpan {
    const Field* fields = nullptr;
    size_t count = 0;
    bool empty() const { return fields == nullptr || count == 0; }
};

// Selects which (unconditional + one chosen branch's) fields apply for a
// payload of the given length/direction/variant. Exposed for callers that
// want to inspect the chosen field set directly (e.g. a GUI).
std::vector<const Field*> SelectBranch(FieldSpan fields, size_t payload_len,
                                        std::optional<uint8_t> packet_type = std::nullopt,
                                        const std::string& variant = "");

// Decode `payload` according to `fields`. If `fields` is empty, returns a
// single {"raw": payload} entry -- nothing is known about this command's
// structure, but the bytes are still returned to you.
FieldMap DecodePayload(FieldSpan fields, const Bytes& payload,
                        std::optional<uint8_t> packet_type = std::nullopt,
                        const std::string& variant = "");

// Encode `values` into payload bytes according to `fields`. Unspecified
// fields default to all-zero bytes. If `fields` is empty, values.at("raw")
// (a Bytes value) is returned as-is -- this is how you send any command
// with no known structure.
Bytes EncodePayload(FieldSpan fields, const FieldMap& values,
                     std::optional<uint8_t> packet_type = std::nullopt,
                     const std::string& variant = "",
                     std::optional<size_t> total_len = std::nullopt);

// Convenience accessors for pulling typed values back out of a FieldMap.
int64_t GetInt(const FieldMap& m, const std::string& name, int64_t default_value = 0);
double GetDouble(const FieldMap& m, const std::string& name, double default_value = 0.0);
Bytes GetBytes(const FieldMap& m, const std::string& name);
std::string GetString(const FieldMap& m, const std::string& name);

} // namespace duml

#include "duml/codecs.hpp"
#include <algorithm>
#include <cmath>
#include <cstring>
#include <map>
#include <set>

namespace duml {

namespace {

int MaskShift(uint32_t mask) {
    if (mask == 0) return 0;
    int shift = 0;
    while ((mask & 1u) == 0) {
        mask >>= 1;
        ++shift;
    }
    return shift;
}

int64_t UnpackSigned(const uint8_t* p, int size) {
    uint64_t v = 0;
    for (int i = 0; i < size; ++i) v |= (static_cast<uint64_t>(p[i]) << (8 * i));
    // sign-extend
    if (size < 8) {
        uint64_t sign_bit = uint64_t(1) << (size * 8 - 1);
        if (v & sign_bit) v |= ~(sign_bit * 2 - 1);
    }
    return static_cast<int64_t>(v);
}

uint64_t UnpackUnsigned(const uint8_t* p, int size) {
    uint64_t v = 0;
    for (int i = 0; i < size; ++i) v |= (static_cast<uint64_t>(p[i]) << (8 * i));
    return v;
}

void PackLE(uint8_t* out, uint64_t v, int size) {
    for (int i = 0; i < size; ++i) out[i] = static_cast<uint8_t>((v >> (8 * i)) & 0xFF);
}

Value UnpackScalar(const std::string& type, const uint8_t* raw, int size) {
    if (type == "uint8") return Value(int64_t(raw[0]));
    if (type == "int8") return Value(UnpackSigned(raw, 1));
    if (type == "uint16") return Value(int64_t(UnpackUnsigned(raw, 2)));
    if (type == "int16") return Value(UnpackSigned(raw, 2));
    if (type == "uint24") return Value(int64_t(UnpackUnsigned(raw, 3)));
    if (type == "uint32") return Value(int64_t(UnpackUnsigned(raw, 4)));
    if (type == "int32") return Value(UnpackSigned(raw, 4));
    if (type == "uint64") return Value(int64_t(UnpackUnsigned(raw, 8))); // note: truncates top bit vs true uint64
    if (type == "int64") return Value(UnpackSigned(raw, 8));
    if (type == "float") {
        float f; std::memcpy(&f, raw, 4); return Value(double(f));
    }
    if (type == "double") {
        double d; std::memcpy(&d, raw, 8); return Value(d);
    }
    if (type == "ether") {
        char buf[32]; int n = 0;
        for (int i = 0; i < size && i < 6; ++i) {
            n += std::snprintf(buf + n, sizeof(buf) - n, i ? ":%02x" : "%02x", raw[i]);
        }
        return Value(std::string(buf, n));
    }
    if (type == "string") {
        const uint8_t* nul = static_cast<const uint8_t*>(std::memchr(raw, 0, size));
        size_t len = nul ? size_t(nul - raw) : size_t(size);
        return Value(std::string(reinterpret_cast<const char*>(raw), len));
    }
    // "bytes" / unrecognized: raw bytes
    return Value(Bytes(raw, raw + size));
}

int64_t AsInt(const Value& v) {
    if (auto p = std::get_if<int64_t>(&v)) return *p;
    if (auto p = std::get_if<double>(&v)) return static_cast<int64_t>(*p);
    throw CodecError("expected numeric value");
}
double AsDouble(const Value& v) {
    if (auto p = std::get_if<double>(&v)) return *p;
    if (auto p = std::get_if<int64_t>(&v)) return static_cast<double>(*p);
    throw CodecError("expected numeric value");
}
const Bytes& AsBytes(const Value& v) {
    if (auto p = std::get_if<Bytes>(&v)) return *p;
    throw CodecError("expected bytes value");
}
const std::string& AsString(const Value& v) {
    if (auto p = std::get_if<std::string>(&v)) return *p;
    throw CodecError("expected string value");
}

void PackScalar(const std::string& type, const Value& value, uint8_t* out, int size) {
    if (type == "float") {
        float f = static_cast<float>(AsDouble(value));
        std::memcpy(out, &f, 4);
        return;
    }
    if (type == "double") {
        double d = AsDouble(value);
        std::memcpy(out, &d, 8);
        return;
    }
    if (type == "bytes" || type.empty()) {
        if (auto p = std::get_if<Bytes>(&value)) {
            int n = std::min<int>(size, int(p->size()));
            std::memcpy(out, p->data(), n);
            for (int i = n; i < size; ++i) out[i] = 0;
        } else {
            uint64_t v = static_cast<uint64_t>(AsInt(value));
            PackLE(out, v, size);
        }
        return;
    }
    if (type == "string") {
        const std::string& s = AsString(value);
        int n = std::min<int>(size, int(s.size()));
        std::memcpy(out, s.data(), n);
        for (int i = n; i < size; ++i) out[i] = 0;
        return;
    }
    if (type == "ether") {
        // "aa:bb:cc:dd:ee:ff" -> 6 raw bytes
        const std::string& s = AsString(value);
        int n = 0;
        size_t pos = 0;
        while (pos < s.size() && n < size) {
            out[n++] = static_cast<uint8_t>(std::stoul(s.substr(pos, 2), nullptr, 16));
            pos += 3; // skip "XX:"
        }
        for (int i = n; i < size; ++i) out[i] = 0;
        return;
    }
    // integer types
    uint64_t v = static_cast<uint64_t>(AsInt(value));
    PackLE(out, v, size);
}

// Parse "payload:len() >= N" style branch text. Returns {matched, result}.
struct LenCond { bool matched; bool result; };
LenCond EvalLenBranch(const std::string& branch, size_t payload_len) {
    size_t p = branch.find("payload:len()");
    if (p == std::string::npos) return {false, false};
    p += std::strlen("payload:len()");
    while (p < branch.size() && branch[p] == ' ') ++p;
    std::string op;
    if (branch.compare(p, 2, ">=") == 0) op = ">=";
    else if (branch.compare(p, 2, "<=") == 0) op = "<=";
    else if (branch.compare(p, 2, "==") == 0) op = "==";
    else if (p < branch.size() && branch[p] == '>') op = ">";
    else if (p < branch.size() && branch[p] == '<') op = "<";
    else return {false, false};
    p += op.size();
    while (p < branch.size() && branch[p] == ' ') ++p;
    size_t start = p;
    while (p < branch.size() && std::isdigit(static_cast<unsigned char>(branch[p]))) ++p;
    if (p == start) return {false, false};
    long n = std::stol(branch.substr(start, p - start));
    bool result;
    if (op == ">=") result = payload_len >= static_cast<size_t>(n);
    else if (op == "<=") result = payload_len <= static_cast<size_t>(n);
    else if (op == "==") result = payload_len == static_cast<size_t>(n);
    else if (op == ">") result = payload_len > static_cast<size_t>(n);
    else result = payload_len < static_cast<size_t>(n);
    return {true, result};
}

struct Slot {
    int offset;
    int size;
    std::vector<const Field*> members;
};

std::vector<Slot> GroupIntoSlots(const std::vector<const Field*>& fields) {
    std::vector<Slot> slots;
    std::map<std::pair<int, int>, size_t> index;
    for (const Field* f : fields) {
        auto key = std::make_pair(f->offset, f->size);
        auto it = index.find(key);
        if (it == index.end()) {
            index[key] = slots.size();
            slots.push_back(Slot{f->offset, f->size, {f}});
        } else {
            slots[it->second].members.push_back(f);
        }
    }
    return slots;
}

} // namespace

std::vector<const Field*> SelectBranch(FieldSpan fields, size_t payload_len,
                                        std::optional<uint8_t> packet_type,
                                        const std::string& variant) {
    std::vector<const Field*> base;
    std::map<std::string, std::vector<const Field*>> groups; // branch text -> fields, insertion order via vector below
    std::vector<std::string> group_order;

    for (size_t i = 0; i < fields.count; ++i) {
        const Field& f = fields.fields[i];
        std::string branch = f.branch ? f.branch : "";
        if (branch.empty()) {
            base.push_back(&f);
        } else {
            if (groups.find(branch) == groups.end()) group_order.push_back(branch);
            groups[branch].push_back(&f);
        }
    }
    if (groups.empty()) return base;

    if (!variant.empty()) {
        for (const auto& label : group_order) {
            if (label.find(variant) != std::string::npos) {
                auto out = base;
                out.insert(out.end(), groups[label].begin(), groups[label].end());
                return out;
            }
        }
        throw CodecError("no branch matching variant: " + variant);
    }

    if (packet_type.has_value()) {
        std::string want = (*packet_type == 0) ? "pack_type == 0" : "pack_type == 1";
        for (const auto& label : group_order) {
            if (label.find(want) != std::string::npos) {
                auto out = base;
                out.insert(out.end(), groups[label].begin(), groups[label].end());
                return out;
            }
        }
        for (const auto& label : group_order) {
            bool req_match = (label.find("Request") != std::string::npos) && (*packet_type == 0);
            bool resp_match = (label.find("Response") != std::string::npos) && (*packet_type == 1);
            if (req_match || resp_match) {
                auto out = base;
                out.insert(out.end(), groups[label].begin(), groups[label].end());
                return out;
            }
        }
    }

    // length-based selection: rank 0 = definitely matches (len-condition true,
    // or no len-condition but fits within payload_len); rank 1 = doesn't fit.
    // Among rank-0 candidates, prefer the biggest declared span (closest fit).
    const std::vector<const Field*>* best = nullptr;
    int best_rank = 2;
    size_t best_span = 0;
    for (const auto& label : group_order) {
        const auto& flds = groups[label];
        size_t span = 0;
        for (const Field* f : flds) span = std::max(span, size_t(f->offset + f->size));
        LenCond lc = EvalLenBranch(label, payload_len);
        int rank;
        if (lc.matched) {
            rank = lc.result ? 0 : 2; // explicit false -> excluded entirely
        } else {
            rank = (span <= payload_len) ? 0 : 1;
        }
        if (rank > 1) continue; // excluded
        if (rank < best_rank || (rank == best_rank && span > best_span)) {
            best_rank = rank;
            best_span = span;
            best = &flds;
        }
    }
    if (best == nullptr) return base;
    auto out = base;
    out.insert(out.end(), best->begin(), best->end());
    return out;
}

FieldMap DecodePayload(FieldSpan fields, const Bytes& payload,
                        std::optional<uint8_t> packet_type, const std::string& variant) {
    FieldMap out;
    if (fields.empty()) {
        out["raw"] = Value(payload);
        return out;
    }
    auto chosen = SelectBranch(fields, payload.size(), packet_type, variant);
    for (const Slot& slot : GroupIntoSlots(chosen)) {
        size_t end = size_t(slot.offset) + size_t(slot.size);
        if (end > payload.size()) continue;
        const uint8_t* raw = payload.data() + slot.offset;
        if (slot.members.size() == 1 && slot.members[0]->mask == 0) {
            const Field* f = slot.members[0];
            out[f->name] = UnpackScalar(f->type ? f->type : "bytes", raw, slot.size);
            continue;
        }
        uint64_t raw_int = UnpackUnsigned(raw, slot.size);
        for (const Field* f : slot.members) {
            if (f->mask != 0) {
                int shift = MaskShift(f->mask);
                out[f->name] = Value(int64_t((raw_int & f->mask) >> shift));
            } else {
                out[f->name] = Value(int64_t(raw_int));
            }
        }
    }
    return out;
}

Bytes EncodePayload(FieldSpan fields, const FieldMap& values,
                     std::optional<uint8_t> packet_type, const std::string& variant,
                     std::optional<size_t> total_len) {
    if (fields.empty()) {
        auto it = values.find("raw");
        if (it == values.end()) return Bytes();
        return AsBytes(it->second);
    }

    size_t inferred_len;
    if (total_len.has_value()) {
        inferred_len = *total_len;
    } else {
        inferred_len = 0;
        for (size_t i = 0; i < fields.count; ++i) {
            const Field& f = fields.fields[i];
            if (values.count(f.name)) {
                inferred_len = std::max(inferred_len, size_t(f.offset + f.size));
            }
        }
    }

    auto chosen = SelectBranch(fields, inferred_len, packet_type, variant);
    if (chosen.empty()) return Bytes();

    size_t span = 0;
    for (const Field* f : chosen) span = std::max(span, size_t(f->offset + f->size));
    Bytes buf(span, 0);

    for (const Slot& slot : GroupIntoSlots(chosen)) {
        if (slot.members.size() == 1 && slot.members[0]->mask == 0) {
            const Field* f = slot.members[0];
            auto it = values.find(f->name);
            if (it != values.end()) {
                PackScalar(f->type ? f->type : "bytes", it->second, buf.data() + slot.offset, slot.size);
            }
            continue;
        }
        uint64_t raw_int = 0;
        // an explicit whole-slot value (a mask==0 member the caller set
        // directly) seeds the base; then OR in the masked sub-fields.
        for (const Field* f : slot.members) {
            if (f->mask == 0) {
                auto it = values.find(f->name);
                if (it != values.end()) raw_int = static_cast<uint64_t>(AsInt(it->second));
            }
        }
        for (const Field* f : slot.members) {
            if (f->mask == 0) continue;
            auto it = values.find(f->name);
            if (it == values.end()) continue;
            int shift = MaskShift(f->mask);
            uint64_t mv = f->mask;
            raw_int = (raw_int & ~mv) | ((static_cast<uint64_t>(AsInt(it->second)) << shift) & mv);
        }
        PackLE(buf.data() + slot.offset, raw_int, slot.size);
    }
    return buf;
}

int64_t GetInt(const FieldMap& m, const std::string& name, int64_t default_value) {
    auto it = m.find(name);
    if (it == m.end()) return default_value;
    return AsInt(it->second);
}
double GetDouble(const FieldMap& m, const std::string& name, double default_value) {
    auto it = m.find(name);
    if (it == m.end()) return default_value;
    return AsDouble(it->second);
}
Bytes GetBytes(const FieldMap& m, const std::string& name) {
    auto it = m.find(name);
    if (it == m.end()) return Bytes();
    return AsBytes(it->second);
}
std::string GetString(const FieldMap& m, const std::string& name) {
    auto it = m.find(name);
    if (it == m.end()) return std::string();
    return AsString(it->second);
}

} // namespace duml

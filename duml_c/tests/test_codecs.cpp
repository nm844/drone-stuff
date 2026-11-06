#include "test_harness.hpp"
#include "duml/codecs.hpp"
#include "duml/registry.hpp"
using namespace duml;

static FieldMap I(std::initializer_list<std::pair<const char*, int64_t>> l) {
    FieldMap m; for (auto& p : l) m[p.first] = Value(p.second); return m;
}

TEST(GimbalControlRoundTrip) {
    auto* spec = LookupCommand(0x04, 0x01);
    Bytes p = EncodePayload(spec->fields, I({{"gimbal_control_unkn0",1024},{"gimbal_control_unkn1",500},{"gimbal_control_unkn2",900}}));
    EXPECT_EQ(p.size(), size_t(6));
    auto d = DecodePayload(spec->fields, p);
    EXPECT_EQ(GetInt(d, "gimbal_control_unkn0"), 1024);
    EXPECT_EQ(GetInt(d, "gimbal_control_unkn2"), 900);
}
TEST(GimbalControlOptionalPaddingBranch) {
    auto* spec = LookupCommand(0x04, 0x01);
    FieldMap m = I({{"gimbal_control_unkn0",1},{"gimbal_control_unkn1",2},{"gimbal_control_unkn2",3}});
    m["gimbal_control_padding"] = Value(Bytes{0, 0});
    Bytes p = EncodePayload(spec->fields, m);
    EXPECT_EQ(p.size(), size_t(8));
}
TEST(RcPushParamBitfieldsRoundTrip) {
    auto* spec = LookupCommand(0x06, 0x05);
    FieldMap m = I({{"rc_push_param_aileron",1500},{"rc_push_param_elevator",1500},{"rc_push_param_throttle",1000},
        {"rc_push_param_rudder",1500},{"rc_push_param_gyro_value",0},
        {"rc_push_param_wheel_click_status",1},{"rc_push_param_wheel_offset",0x1F},
        {"rc_push_param_not_wheel_positive",1},{"rc_push_param_wheel_changed",1},
        {"rc_push_param_go_home_button_pressed",1},{"rc_push_param_mode",3},{"rc_push_param_get_foot_stool",2}});
    auto d = DecodePayload(spec->fields, EncodePayload(spec->fields, m));
    for (auto& [k, v] : m) EXPECT_EQ(GetInt(d, k), std::get<int64_t>(v));
}
TEST(BitfieldMergeDoesNotClobberSiblings) {
    auto* spec = LookupCommand(0x06, 0x05);
    FieldMap base = I({{"rc_push_param_aileron",0},{"rc_push_param_elevator",0},{"rc_push_param_throttle",0},{"rc_push_param_rudder",0},{"rc_push_param_gyro_value",0}});
    FieldMap v1 = base; v1["rc_push_param_wheel_click_status"] = Value(int64_t(1)); v1["rc_push_param_wheel_offset"] = Value(int64_t(0));
    FieldMap v2 = base; v2["rc_push_param_wheel_click_status"] = Value(int64_t(0)); v2["rc_push_param_wheel_offset"] = Value(int64_t(0x1F));
    auto d1 = DecodePayload(spec->fields, EncodePayload(spec->fields, v1));
    auto d2 = DecodePayload(spec->fields, EncodePayload(spec->fields, v2));
    EXPECT_EQ(GetInt(d1, "rc_push_param_wheel_click_status"), 1);
    EXPECT_EQ(GetInt(d1, "rc_push_param_wheel_offset"), 0);
    EXPECT_EQ(GetInt(d2, "rc_push_param_wheel_click_status"), 0);
    EXPECT_EQ(GetInt(d2, "rc_push_param_wheel_offset"), 0x1F);
}
TEST(UnknownCommandRawPassthrough) {
    Bytes raw = {0xDE, 0xAD, 0xBE, 0xEF};
    FieldMap m; m["raw"] = Value(raw);
    EXPECT_TRUE(EncodePayload(FieldSpan{}, m) == raw);
    auto d = DecodePayload(FieldSpan{}, raw);
    EXPECT_TRUE(GetBytes(d, "raw") == raw);
}
TEST(UnknownVariantThrows) {
    auto* spec = LookupCommand(0x04, 0x01);
    EXPECT_THROWS(EncodePayload(spec->fields, FieldMap{}, std::nullopt, "no_such_branch_xyz"));
}
TEST(BatteryPushCommonInfoRoundTrip) {
    auto* spec = LookupCommand(0x0d, 0x06);
    FieldMap m = I({{"design_capacity",6000},{"full_charge_capacity",5800},{"remaining_capacity",3000},{"pack_voltage",15400},
        {"current",-2500},{"life_percentage",96},{"capacity_percentage",51},{"temperature",253},{"cycle_count",42},
        {"serial_number",0x1234},{"cell1",3850},{"cell2",3851},{"cell3",3849},{"cell4",3850},{"cell5",3848},{"cell6",3852},
        {"average_current",-2400},{"unknown20",0},{"error_count",0},{"n_discharge_times",42},{"current_status",0}});
    Bytes p = EncodePayload(spec->fields, m);
    EXPECT_EQ(p.size(), size_t(45));
    auto d = DecodePayload(spec->fields, p);
    for (auto& [k, v] : m) EXPECT_EQ(GetInt(d, k), std::get<int64_t>(v));
}

TEST_MAIN()

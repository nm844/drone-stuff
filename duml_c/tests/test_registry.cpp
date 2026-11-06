#include "test_harness.hpp"
#include "duml/registry.hpp"
#include <cstring>
using namespace duml;

TEST(LoadsExpectedCounts) {
    auto s = GetRegistryStats();
    EXPECT_EQ(s.total, size_t(877));
    EXPECT_EQ(s.full, size_t(157));
}
TEST(PingLookup) {
    auto* c = LookupCommand(0, 0);
    EXPECT_TRUE(c != nullptr);
    EXPECT_TRUE(std::strcmp(c->name, "Ping") == 0);
}
TEST(UnregisteredStub) {
    auto c = RequireCommand(0x1F, 0xFE);
    EXPECT_TRUE(c.fields.empty());
    EXPECT_TRUE(std::strcmp(c.decode_status, "none") == 0);
}
TEST(NameSearchFindsGimbalControl) { EXPECT_TRUE(!FindByName("gimbal control").empty()); }
TEST(CommandsInSetSorted) {
    auto v = CommandsInSet(4);
    for (size_t i = 1; i < v.size(); ++i) EXPECT_TRUE(v[i-1]->cmd_id < v[i]->cmd_id);
}
TEST(NewDecodesPresent) {
    EXPECT_TRUE(std::strcmp(LookupCommand(0x0d, 0x06)->source, "flyrec_crossref") == 0);
    EXPECT_TRUE(std::strcmp(LookupCommand(0x03, 0x0a)->source, "flyrec_crossref") == 0);
}

TEST_MAIN()

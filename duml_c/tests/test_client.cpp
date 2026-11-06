#include "test_harness.hpp"
#include "duml/client.hpp"
using namespace duml;

class Loopback : public Transport {
public:
    void Write(const uint8_t* d, size_t n) override { buf.insert(buf.end(), d, d + n); }
    std::vector<uint8_t> Read(size_t max, int) override {
        size_t n = std::min(max, buf.size());
        std::vector<uint8_t> o(buf.begin(), buf.begin() + n);
        buf.erase(buf.begin(), buf.begin() + n);
        return o;
    }
    std::vector<uint8_t> buf;
};

TEST(SendThenPumpDecodesNamedFields) {
    Loopback t; DumlClient c(t, 2);
    BuildOptions o; o.receiver_type = 4;
    o.fields["gimbal_control_unkn0"] = Value(int64_t(1024));
    o.fields["gimbal_control_unkn1"] = Value(int64_t(500));
    o.fields["gimbal_control_unkn2"] = Value(int64_t(900));
    c.SendCommand(0x04, 0x01, o);
    auto frames = c.Pump(10);
    EXPECT_EQ(frames.size(), size_t(1));
    EXPECT_EQ(GetInt(frames[0].fields, "gimbal_control_unkn1"), 500);
}
TEST(RawPayloadForUnknownCommand) {
    Loopback t; DumlClient c(t);
    BuildOptions o; o.raw_payload = Bytes{1, 2, 3};
    c.SendCommand(0x02, 0x01, o);
    auto frames = c.Pump(10);
    EXPECT_EQ(frames.size(), size_t(1));
    EXPECT_TRUE(frames[0].frame.payload == (Bytes{1, 2, 3}));
}
TEST(StreamFramerResyncsPastGarbage) {
    Frame f; f.cmd_set = 0; f.cmd_id = 1; f.seq_num = 7;
    auto enc = f.Encode();
    std::vector<uint8_t> noisy = {0x00, 0x55, 0x01, 0xFF, 0x13};
    noisy.insert(noisy.end(), enc.begin(), enc.end());
    StreamFramer sf; sf.Feed(noisy);
    auto out = sf.PopReady();
    EXPECT_EQ(out.size(), size_t(1));
    EXPECT_EQ(out[0].seq_num, 7);
}
TEST(StreamFramerHandlesFragmentation) {
    Frame f; f.cmd_set = 4; f.cmd_id = 1; f.payload = {1,2,3,4,5,6};
    auto enc = f.Encode();
    StreamFramer sf;
    for (uint8_t b : enc) sf.Feed(&b, 1);
    EXPECT_EQ(sf.PopReady().size(), size_t(1));
}

TEST_MAIN()

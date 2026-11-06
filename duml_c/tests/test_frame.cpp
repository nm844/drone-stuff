#include "test_harness.hpp"
#include "duml/crc.hpp"
#include "duml/frame.hpp"
using namespace duml;

TEST(Crc8TableMatchesFirmware) {
    const uint8_t expect[16] = {0x00,0x5E,0xBC,0xE2,0x61,0x3F,0xDD,0x83,0xC2,0x9C,0x7E,0x20,0xA3,0xFD,0x1F,0x41};
    for (int i = 0; i < 16; ++i) EXPECT_EQ(kCrc8Table[i], expect[i]);
}
TEST(Crc16TableMatchesFirmware) {
    EXPECT_EQ(kCrc16Table[1], 0x1189);
    EXPECT_EQ(kCrc16Table[255], 0x0F78);
}
TEST(Crc16ZeroLengthIs0xFFFF) { EXPECT_EQ(Crc16(nullptr, 0), 0xFFFF); }
TEST(Crc8EmptyReturnsSeed) { EXPECT_EQ(Crc8(nullptr, 0), 0x77); }

TEST(KnownVectorMatchesPythonImplementation) {
    Frame f; f.sender_type = 10; f.receiver_type = 3; f.cmd_set = 0; f.cmd_id = 0; f.seq_num = 0x1234;
    auto enc = f.Encode();
    const uint8_t expect[] = {0x55,0x0d,0x04,0x33,0x0a,0x03,0x34,0x12,0x00,0x00,0x00,0xde,0x22};
    EXPECT_EQ(enc.size(), sizeof(expect));
    for (size_t i = 0; i < sizeof(expect); ++i) EXPECT_EQ(enc[i], expect[i]);
}
TEST(PayloadRoundTrip) {
    Frame f; f.sender_type = 2; f.receiver_type = 4; f.cmd_set = 4; f.cmd_id = 1; f.seq_num = 42;
    f.ack_type = 2; f.packet_type = 1;
    for (int i = 0; i < 32; ++i) f.payload.push_back(uint8_t(i));
    Frame d = Frame::Decode(f.Encode());
    EXPECT_TRUE(d.payload == f.payload);
    EXPECT_EQ(d.ack_type, 2);
    EXPECT_EQ(d.packet_type, 1);
}
TEST(IndexBitsRoundTrip) {
    Frame f; f.sender_type = 5; f.sender_index = 3; f.receiver_type = 7; f.receiver_index = 2; f.cmd_set = 1; f.cmd_id = 1;
    Frame d = Frame::Decode(f.Encode());
    EXPECT_EQ(d.sender_type, 5); EXPECT_EQ(d.sender_index, 3);
    EXPECT_EQ(d.receiver_type, 7); EXPECT_EQ(d.receiver_index, 2);
}
TEST(CorruptedHeaderCrcRejected) {
    Frame f; f.cmd_set = 1; f.cmd_id = 1;
    auto enc = f.Encode(); enc[3] ^= 0xFF;
    EXPECT_THROWS(Frame::Decode(enc));
}
TEST(CorruptedBodyCrcRejected) {
    Frame f; f.cmd_set = 4; f.cmd_id = 1; f.payload = {1,2,3,4};
    auto enc = f.Encode(); enc[12] ^= 0xFF;
    EXPECT_THROWS(Frame::Decode(enc));
}
TEST(BadSofRejected) {
    Frame f; auto enc = f.Encode(); enc[0] = 0;
    EXPECT_THROWS(Frame::Decode(enc));
}
TEST(TooShortRejected) { std::vector<uint8_t> b = {0x55, 0x00}; EXPECT_THROWS(Frame::Decode(b)); }
TEST(EncryptedEncodeRejected) {
    Frame f; f.encrypt_type = 1;
    EXPECT_THROWS(f.Encode());
}
TEST(IterFramesBackToBack) {
    Frame a; a.seq_num = 1; Frame b; b.seq_num = 2; b.cmd_id = 1; b.payload = {0xAA, 0xBB};
    auto ea = a.Encode(); auto eb = b.Encode();
    ea.insert(ea.end(), eb.begin(), eb.end());
    auto frames = IterFrames(ea.data(), ea.size());
    EXPECT_EQ(frames.size(), size_t(2));
    EXPECT_EQ(frames[1].seq_num, 2);
}

TEST_MAIN()

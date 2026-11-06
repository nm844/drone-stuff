// DUML v1 protocol enums. Ground truth confirmed against this project's
// WM260 firmware disassembly -- see ../../DUML_PROTOCOL/00_FRAME_FORMAT.md
#pragma once
#include <cstdint>
#include <string>

namespace duml {

// 5-bit sender/receiver device-type field (frame byte 4 bits0-4, byte 5 bits0-4).
enum class DeviceType : uint8_t {
    kAny = 0, kCamera = 1, kApp = 2, kFlightController = 3, kGimbal = 4,
    kCenterBoard = 5, kRemoteControl = 6, kWifiAir = 7, kDm36xAir = 8,
    kHdMcuAir = 9, kPc = 10, kBattery = 11, kEsc = 12, kDm36xGround = 13,
    kHdMcuGround = 14, kS2pUsbAir = 15, kS2pUsbGround = 16, kMonocular = 17,
    kBinocular = 18, kFpgaAir = 19, kFpgaGround = 20, kSimulator = 21,
    kBaseStation = 22, kAirborneComputing = 23, kRcBattery = 24, kImu = 25,
    kGpsRtk = 26, kWifiGround = 27, kSigCvt = 28, kPmu = 29,
    kUnknown30 = 30, kLast = 31,
};

// 2-bit ack-type field (frame byte 8 bits 5-6).
enum class AckType : uint8_t { kNoAckNeeded = 0, kAckBeforeExec = 1, kAckAfterExec = 2 };

// 3-bit encryption-type field (frame byte 8 bits 0-2).
enum class EncryptType : uint8_t {
    kNone = 0, kAes128 = 1, kSelfDef = 2, kXor = 3,
    kDes56 = 4, kDes112 = 5, kAes192 = 6, kAes256 = 7,
};

// 1-bit packet-type field (frame byte 8 bit 7).
enum class PacketType : uint8_t { kRequest = 0, kResponse = 1 };

// Command-set selector (frame byte 9).
enum class CmdSet : uint8_t {
    kGeneral = 0x00, kSpecial = 0x01, kCamera = 0x02, kFlightControl = 0x03,
    kGimbal = 0x04, kCenterBoard = 0x05, kRemoteControl = 0x06, kWifi = 0x07,
    kDm36x = 0x08, kHdLink = 0x09, kMonoBinocular = 0x0a, kSimulator = 0x0b,
    kEsc = 0x0c, kBattery = 0x0d, kDataLogger = 0x0e, kRtk = 0x0f,
    kAutomation = 0x10, kAdsb = 0x11,
};

const char* CmdSetName(uint8_t cmd_set);
const char* DeviceTypeName(uint8_t device_type);

} // namespace duml

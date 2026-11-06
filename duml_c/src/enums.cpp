#include "duml/enums.hpp"

namespace duml {

const char* CmdSetName(uint8_t cmd_set) {
    switch (cmd_set) {
        case 0x00: return "General";
        case 0x01: return "Special";
        case 0x02: return "Camera";
        case 0x03: return "Flight Control";
        case 0x04: return "Gimbal";
        case 0x05: return "Center Board";
        case 0x06: return "Remote Control";
        case 0x07: return "Wi-Fi";
        case 0x08: return "DM36x";
        case 0x09: return "HD Link";
        case 0x0a: return "Mono/Binocular (Vision)";
        case 0x0b: return "Simulator";
        case 0x0c: return "ESC";
        case 0x0d: return "Battery";
        case 0x0e: return "Data Logger";
        case 0x0f: return "RTK";
        case 0x10: return "Automation";
        case 0x11: return "ADSB";
        default: return "Unknown";
    }
}

const char* DeviceTypeName(uint8_t device_type) {
    switch (static_cast<DeviceType>(device_type)) {
        case DeviceType::kAny: return "ANY";
        case DeviceType::kCamera: return "CAMERA";
        case DeviceType::kApp: return "APP";
        case DeviceType::kFlightController: return "FLIGHT_CONTROLLER";
        case DeviceType::kGimbal: return "GIMBAL";
        case DeviceType::kCenterBoard: return "CENTER_BOARD";
        case DeviceType::kRemoteControl: return "REMOTE_CONTROL";
        case DeviceType::kWifiAir: return "WIFI_AIR";
        case DeviceType::kDm36xAir: return "DM36X_AIR";
        case DeviceType::kHdMcuAir: return "HD_MCU_AIR";
        case DeviceType::kPc: return "PC";
        case DeviceType::kBattery: return "BATTERY";
        case DeviceType::kEsc: return "ESC";
        case DeviceType::kDm36xGround: return "DM36X_GROUND";
        case DeviceType::kHdMcuGround: return "HD_MCU_GROUND";
        case DeviceType::kS2pUsbAir: return "S2P_USB_AIR";
        case DeviceType::kS2pUsbGround: return "S2P_USB_GROUND";
        case DeviceType::kMonocular: return "MONOCULAR";
        case DeviceType::kBinocular: return "BINOCULAR";
        case DeviceType::kFpgaAir: return "FPGA_AIR";
        case DeviceType::kFpgaGround: return "FPGA_GROUND";
        case DeviceType::kSimulator: return "SIMULATOR";
        case DeviceType::kBaseStation: return "BASE_STATION";
        case DeviceType::kAirborneComputing: return "AIRBORNE_COMPUTING";
        case DeviceType::kRcBattery: return "RC_BATTERY";
        case DeviceType::kImu: return "IMU";
        case DeviceType::kGpsRtk: return "GPS_RTK";
        case DeviceType::kWifiGround: return "WIFI_GROUND";
        case DeviceType::kSigCvt: return "SIG_CVT";
        case DeviceType::kPmu: return "PMU";
        case DeviceType::kUnknown30: return "UNKNOWN30";
        case DeviceType::kLast: return "LAST";
        default: return "UNKNOWN";
    }
}

} // namespace duml

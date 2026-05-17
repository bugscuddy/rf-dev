/**
 * Serial Protocol — Message format between C++ firmware and Python AI layer.
 *
 * C++ (firmware) owns the hardware: I2C, GPIO, radio, power management.
 * Python (AI) owns the intelligence: routing, API, mesh logic.
 *
 * They communicate via UART (115200 baud) using newline-delimited JSON.
 *
 * C++ -> Python messages:
 *   {"type":"power","harvested_mw":150.5,"battery_v":3.7,"mode":"Reduced"}
 *   {"type":"radio","tvws_connected":true,"frequency_mhz":574,"rssi_dbm":-65}
 *   {"type":"heartbeat","uptime_sec":3600,"neighbors":3}
 *   {"type":"alert","code":"LOW_POWER","message":"Entering sleep mode"}
 *
 * Python -> C++ messages:
 *   {"type":"cmd_gateway","enabled":true}
 *   {"type":"cmd_power","mode":"FullOperation"}
 *   {"type":"cmd_tvws","frequency_mhz":574,"bandwidth_mhz":6}
 */

#ifndef SERIAL_PROTOCOL_H
#define SERIAL_PROTOCOL_H

#include <ArduinoJson.h>

namespace SerialProtocol {

// Maximum size for a single JSON message (bytes)
constexpr size_t MAX_MESSAGE_SIZE = 512;

// Message types from firmware -> Python
constexpr const char* MSG_POWER     = "power";
constexpr const char* MSG_RADIO     = "radio";
constexpr const char* MSG_HEARTBEAT = "heartbeat";
constexpr const char* MSG_ALERT     = "alert";

// Command types from Python -> firmware
constexpr const char* CMD_GATEWAY   = "cmd_gateway";
constexpr const char* CMD_POWER     = "cmd_power";
constexpr const char* CMD_TVWS      = "cmd_tvws";

/**
 * Build a power status message.
 * @param harvested_mw  Power harvested from ambient sources (mW)
 * @param battery_v     Storage capacitor / battery voltage (V)
 * @param mode          Power mode string: FullOperation, Reduced, LowPower, Sleep
 * @return JSON document (call serializeJson to stringify)
 */
JsonDocument buildPowerMessage(float harvested_mw, float battery_v, const char* mode);

/**
 * Build a radio/TVWS status message.
 */
JsonDocument buildRadioMessage(bool connected, float frequency_mhz, float bandwidth_mhz, float rssi_dbm);

/**
 * Build a heartbeat message.
 */
JsonDocument buildHeartbeatMessage(uint32_t uptime_sec, uint8_t neighbor_count);

/**
 * Build an alert message.
 */
JsonDocument buildAlertMessage(const char* code, const char* message);

/**
 * Parse an incoming command from Python.
 * @param json  Raw JSON string (null-terminated)
 * @param doc   Output ArduinoJson document
 * @return true if valid JSON was parsed
 */
bool parseCommand(const char* json, JsonDocument& doc);

/**
 * Send a JSON document over Serial (appends newline).
 */
void sendJson(const JsonDocument& doc);

} // namespace SerialProtocol

#endif // SERIAL_PROTOCOL_H

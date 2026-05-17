#include "serial_protocol.h"
#include <Arduino.h>

namespace SerialProtocol {

JsonDocument buildPowerMessage(float harvested_mw, float battery_v, const char* mode) {
    JsonDocument doc;
    doc["type"] = MSG_POWER;
    doc["harvested_mw"] = round(harvested_mw * 100.0) / 100.0;
    doc["battery_v"] = round(battery_v * 100.0) / 100.0;
    doc["mode"] = mode;
    return doc;
}

JsonDocument buildRadioMessage(bool connected, float frequency_mhz, float bandwidth_mhz, float rssi_dbm) {
    JsonDocument doc;
    doc["type"] = MSG_RADIO;
    doc["tvws_connected"] = connected;
    doc["frequency_mhz"] = frequency_mhz;
    doc["bandwidth_mhz"] = bandwidth_mhz;
    doc["rssi_dbm"] = rssi_dbm;
    return doc;
}

JsonDocument buildHeartbeatMessage(uint32_t uptime_sec, uint8_t neighbor_count) {
    JsonDocument doc;
    doc["type"] = MSG_HEARTBEAT;
    doc["uptime_sec"] = uptime_sec;
    doc["neighbors"] = neighbor_count;
    return doc;
}

JsonDocument buildAlertMessage(const char* code, const char* message) {
    JsonDocument doc;
    doc["type"] = MSG_ALERT;
    doc["code"] = code;
    doc["message"] = message;
    return doc;
}

bool parseCommand(const char* json, JsonDocument& doc) {
    DeserializationError err = deserializeJson(doc, json);
    return err == DeserializationError::Ok && doc["type"].is<const char*>();
}

void sendJson(const JsonDocument& doc) {
    serializeJson(doc, Serial);
    Serial.println();  // newline delimiter
}

} // namespace SerialProtocol

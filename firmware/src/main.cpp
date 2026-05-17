/**
 * Meshwork Firmware — Main Entry Point
 *
 * Bare-metal C++ firmware for ESP32-S3 / nRF9160 / GL.iNet.
 *
 * Responsibilities (per architecture principle: C++ owns hardware):
 *   - Power management: sleep/wake, I2C energy IC, watchdog
 *   - Radio control: TVWS module init, channel scanning
 *   - Boot sequence: initialize all hardware before Python starts
 *   - Serial protocol: JSON messages over UART to Python AI layer
 *
 * DOES NOT do: AI routing, API serving, mesh logic — that stays in Python.
 */

#include <Arduino.h>
#include <Wire.h>
#include "power_manager.h"
#include "radio_manager.h"
#include "serial_protocol.h"

// --- Timing Constants ---
constexpr uint32_t HEARTBEAT_INTERVAL_MS = 30000;   // 30 seconds
constexpr uint32_t POWER_REPORT_INTERVAL_MS = 5000;  // 5 seconds
constexpr uint32_t RADIO_REPORT_INTERVAL_MS = 10000; // 10 seconds
constexpr uint32_t WATCHDOG_FEED_INTERVAL_MS = 1000; // 1 second

// --- State ---
static uint32_t g_boot_time_ms = 0;
static uint32_t g_last_heartbeat = 0;
static uint32_t g_last_power_report = 0;
static uint32_t g_last_radio_report = 0;
static uint32_t g_last_watchdog_feed = 0;
static uint8_t  g_neighbor_count = 0;  // Python tells us this via serial

// --- Serial Buffer ---
// Fixed-size buffer per coding standard: no dynamic allocation in ISR paths
static char g_serial_buf[SerialProtocol::MAX_MESSAGE_SIZE];
static size_t g_serial_buf_len = 0;

void processSerialCommand(const char* json) {
    JsonDocument doc;
    if (!SerialProtocol::parseCommand(json, doc)) return;

    const char* type = doc["type"];
    if (!type) return;

    if (strcmp(type, SerialProtocol::CMD_GATEWAY) == 0) {
        bool enabled = doc["enabled"] | false;
        // Store gateway state — Python will query it
        // In production: set a GPIO that Python can read, or store in RTC memory
        // For now: acknowledge
        JsonDocument ack;
        ack["type"] = "ack";
        ack["cmd"] = "gateway";
        ack["enabled"] = enabled;
        SerialProtocol::sendJson(ack);
    }
    else if (strcmp(type, SerialProtocol::CMD_POWER) == 0) {
        const char* mode_str = doc["mode"] | "FullOperation";
        Power::Mode mode = Power::Mode::FULL;
        if (strcmp(mode_str, "Reduced") == 0)     mode = Power::Mode::REDUCED;
        else if (strcmp(mode_str, "LowPower") == 0) mode = Power::Mode::LOW_POWER;
        else if (strcmp(mode_str, "Sleep") == 0)    mode = Power::Mode::SLEEP;
        Power::applyMode(mode);
    }
    else if (strcmp(type, SerialProtocol::CMD_TVWS) == 0) {
        float freq = doc["frequency_mhz"] | 574.0f;
        float bw = doc["bandwidth_mhz"] | 6.0f;
        Radio::Channel ch = {freq, bw, Radio::MAX_TX_POWER_DBM, false, 25.0f};
        Radio::connect(ch);
    }
}

void readSerialCommands() {
    while (Serial.available()) {
        char c = Serial.read();
        if (c == '\n') {
            g_serial_buf[g_serial_buf_len] = '\0';
            processSerialCommand(g_serial_buf);
            g_serial_buf_len = 0;
        }
        else if (g_serial_buf_len < SerialProtocol::MAX_MESSAGE_SIZE - 1) {
            g_serial_buf[g_serial_buf_len++] = c;
        }
        // Overflow: reset buffer (corrupted message)
        else {
            g_serial_buf_len = 0;
        }
    }
}

void setup() {
    // Initialize serial BEFORE anything else — needed for boot logging
    // 115200 baud is the sweet spot: fast enough for JSON, reliable over 3ft wires
    Serial.begin(115200);

    // Wait up to 2 seconds for serial monitor connection (development only)
    uint32_t wait_start = millis();
    while (!Serial && (millis() - wait_start < 2000)) {
        ;  // ESP32 USB CDC may need time to enumerate
    }

    Serial.println();
    Serial.println("{\"type\":\"boot\",\"message\":\"Meshwork Firmware v0.1 booting...\"}");

    // --- Boot Sequence ---
    // Step 1: Initialize power subsystem (I2C, energy IC, set initial mode)
    bool power_ok = Power::init();
    if (power_ok) {
        float power_mw = Power::readHarvestedPower_mW();
        Power::Mode mode = Power::getModeFromPower(power_mw);
        Power::applyMode(mode);
        Serial.print("{\"type\":\"boot\",\"message\":\"Power IC detected, mode=");
        Serial.print(Power::modeToString(mode));
        Serial.println("\"}");
    } else {
        Serial.println("{\"type\":\"boot\",\"message\":\"No energy IC — simulation mode\"}");
    }

    // Step 2: Initialize radio subsystem
    bool radio_ok = Radio::init();
    if (radio_ok) {
        Radio::Channel best;
        if (Radio::selectBestChannel(best)) {
            Radio::connect(best);
            Serial.print("{\"type\":\"boot\",\"message\":\"Radio connected, freq=");
            Serial.print(best.frequency_mhz);
            Serial.println("\"}");
        }
    }

    // Step 3: Record boot time for uptime tracking
    g_boot_time_ms = millis();

    // Step 4: Boot complete — signal Python that firmware is ready
    JsonDocument ready_msg;
    ready_msg["type"] = "ready";
    ready_msg["firmware_version"] = "0.1.0";
    ready_msg["hardware"] = "esp32s3";
    ready_msg["power_ic"] = power_ok ? "AEM10941" : "simulation";
    ready_msg["radio"] = radio_ok ? "TVWS" : "simulation";
    SerialProtocol::sendJson(ready_msg);
}

void loop() {
    uint32_t now = millis();

    // 1. Feed watchdog (must happen at least every 2 seconds)
    if (now - g_last_watchdog_feed >= WATCHDOG_FEED_INTERVAL_MS) {
        Power::feedWatchdog();
        g_last_watchdog_feed = now;
    }

    // 2. Read and process commands from Python layer
    readSerialCommands();

    // 3. Report power status (every 5 seconds)
    if (now - g_last_power_report >= POWER_REPORT_INTERVAL_MS) {
        float harvested_mw = Power::readHarvestedPower_mW();
        float battery_v = Power::readBatteryVoltage_V();
        Power::Mode mode = Power::getModeFromPower(harvested_mw);
        Power::applyMode(mode);  // auto-transition if power changed

        auto msg = SerialProtocol::buildPowerMessage(
            harvested_mw, battery_v, Power::modeToString(mode)
        );
        SerialProtocol::sendJson(msg);
        g_last_power_report = now;
    }

    // 4. Report radio status (every 10 seconds)
    if (now - g_last_radio_report >= RADIO_REPORT_INTERVAL_MS) {
        auto status = Radio::getLinkStatus();
        if (status.connected) {
            auto msg = SerialProtocol::buildRadioMessage(
                true, status.frequency_mhz, Radio::CHANNEL_BW_MHZ, status.rssi_dbm
            );
            SerialProtocol::sendJson(msg);
        }
        g_last_radio_report = now;
    }

    // 5. Heartbeat (every 30 seconds)
    if (now - g_last_heartbeat >= HEARTBEAT_INTERVAL_MS) {
        uint32_t uptime_sec = (now - g_boot_time_ms) / 1000;
        auto msg = SerialProtocol::buildHeartbeatMessage(uptime_sec, g_neighbor_count);
        SerialProtocol::sendJson(msg);
        g_last_heartbeat = now;
    }

    // 6. Yield to lower-priority tasks (FreeRTOS idle, WiFi stack, etc.)
    // On ESP32, delay(1) yields to other FreeRTOS tasks without busy-waiting
    delay(1);
}

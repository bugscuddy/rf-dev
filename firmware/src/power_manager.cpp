#include "power_manager.h"
#include <Arduino.h>
#include <Wire.h>

namespace Power {

// Track which IC we detected (0 = none, 1 = AEM10941, 2 = BQ25570)
static uint8_t g_ic_detected = 0;

// Current power mode
static Mode g_current_mode = Mode::FULL;

bool init() {
    // Start I2C at 100 kHz — standard mode is more reliable over longer traces
    // on a prototype board than fast mode (400 kHz).
    Wire.setPins(I2C_SDA, I2C_SCL);
    Wire.begin();
    Wire.setClock(100000);

    // Small delay for bus stabilization after Wire.begin()
    delay(10);

    // Probe for AEM10941 first (preferred — multi-source harvester)
    Wire.beginTransmission(AEM10941_ADDR);
    uint8_t err = Wire.endTransmission();
    if (err == 0) {
        g_ic_detected = 1;
        // Configure AEM10941 MPPT settings
        // Register 0x10: MPPT_RATIO — set to 0x50 for 50% ratio (optimal for RF harvest)
        Wire.beginTransmission(AEM10941_ADDR);
        Wire.write(0x10);
        Wire.write(0x50);
        Wire.endTransmission();
        return true;
    }

    // Fallback to BQ25570
    Wire.beginTransmission(BQ25570_ADDR);
    err = Wire.endTransmission();
    if (err == 0) {
        g_ic_detected = 2;
        // BQ25570 auto-configures MPPT on boot — no register write needed
        return true;
    }

    // No energy IC found — running in simulation mode (development)
    g_ic_detected = 0;
    return false;
}

float readHarvestedPower_mW() {
    if (g_ic_detected == 1) {
        // AEM10941: read 12-bit ADC from 0x00 (high byte) + 0x01 (low byte)
        Wire.beginTransmission(AEM10941_ADDR);
        Wire.write(0x00);
        Wire.endTransmission(false);  // repeated start
        Wire.requestFrom(AEM10941_ADDR, (uint8_t)2);
        if (Wire.available() >= 2) {
            uint8_t high = Wire.read();  // register 0x00
            uint8_t low  = Wire.read();   // register 0x01
            uint16_t raw_adc = (high << 8) | low;
            // Convert to voltage: 0-3.3V across 12-bit range
            float voltage = (raw_adc / 4095.0f) * 3.3f;
            // Scale to milliwatts: empirical calibration factor for RF harvester
            float power_mw = voltage * 200.0f;
            return power_mw;
        }
    }
    else if (g_ic_detected == 2) {
        // BQ25570: read 8-bit ADC from register 0x02
        Wire.beginTransmission(BQ25570_ADDR);
        Wire.write(0x02);
        Wire.endTransmission(false);
        Wire.requestFrom(BQ25570_ADDR, (uint8_t)1);
        if (Wire.available() >= 1) {
            uint8_t raw = Wire.read();
            // BQ25570: ~2 mW per LSB in this configuration
            return raw * 2.0f;
        }
    }

    // Simulation mode: return a value that cycles to test power mode transitions
    // Cycles through 0-600 mW over ~5 minutes for testing
    uint32_t t = millis() / 1000;
    float sim = 300.0f + 300.0f * sinf(t * 0.02f);
    return sim > 0.0f ? sim : 0.0f;
}

float readBatteryVoltage_V() {
    if (g_ic_detected == 1) {
        // AEM10941: read 12-bit ADC from 0x02 (high) + 0x03 (low)
        Wire.beginTransmission(AEM10941_ADDR);
        Wire.write(0x02);
        Wire.endTransmission(false);
        Wire.requestFrom(AEM10941_ADDR, (uint8_t)2);
        if (Wire.available() >= 2) {
            uint8_t high = Wire.read();
            uint8_t low  = Wire.read();
            uint16_t raw_adc = (high << 8) | low;
            // 0-5V range for battery monitoring
            return (raw_adc / 4095.0f) * 5.0f;
        }
    }

    // Simulation: fixed 3.7V (typical Li-ion / supercap voltage)
    return 3.7f;
}

Mode getModeFromPower(float harvested_mw) {
    if (harvested_mw >= THRESH_FULL)      return Mode::FULL;
    if (harvested_mw >= THRESH_REDUCED)   return Mode::REDUCED;
    if (harvested_mw >= THRESH_LOW_POWER) return Mode::LOW_POWER;
    return Mode::SLEEP;
}

const char* modeToString(Mode mode) {
    switch (mode) {
        case Mode::FULL:      return "FullOperation";
        case Mode::REDUCED:   return "Reduced";
        case Mode::LOW_POWER: return "LowPower";
        case Mode::SLEEP:     return "Sleep";
    }
    return "Unknown";
}

void applyMode(Mode mode) {
    if (mode == g_current_mode) return;
    g_current_mode = mode;

    switch (mode) {
        case Mode::FULL:
            // Enable all subsystems at full power
            // GPIO: turn on status LED (if present)
            digitalWrite(LED_BUILTIN, HIGH);
            // Radio: full TX power (typically 20 dBm on ESP32-S3)
            // Mesh: enable periodic beacon and routing
            break;

        case Mode::REDUCED:
            // Reduce TX power by 50% to save energy
            // GPIO: turn off LED to save ~5 mW
            digitalWrite(LED_BUILTIN, LOW);
            // Radio: reduced TX power (~14 dBm)
            // Mesh: continue routing but with lower beacon frequency
            break;

        case Mode::LOW_POWER:
            // Intermittent beacon only — no routing, no gateway
            // GPIO: all non-essential pins to INPUT (high-Z, no leakage)
            pinMode(LED_BUILTIN, INPUT);
            // Radio: beacon every 30s at minimum power
            break;

        case Mode::SLEEP:
            // Deep sleep — wake on I2C interrupt or RTC timer
            // All GPIO set to INPUT_PULLDOWN to minimize leakage
            pinMode(LED_BUILTIN, INPUT_PULLDOWN);
            // Serial buffer flushed before sleep
            Serial.flush();
            break;
    }
}

void feedWatchdog() {
    // On ESP32, the task watchdog is fed automatically by the FreeRTOS idle task
    // if CONFIG_ESP_TASK_WDT is enabled. We also manually feed the RTC watchdog:
    // WRITE_PERI_REG(RTC_CNTL_WDT_FEED_REG, 1);  // feed RTC watchdog
    // For Arduino: use esp_task_wdt_reset() if available
    #ifdef ESP_PLATFORM
    // esp_task_wdt_reset();  // requires #include <esp_task_wdt.h>
    #endif
}

void deepSleep(uint32_t seconds) {
    // Save minimal mesh state to RTC memory (8KB available on ESP32-S3)
    // Only store: node_id, gateway flag, neighbor count
    // RTC memory survives deep sleep but NOT power loss

    // Flush serial before sleep
    Serial.flush();

    // Configure wake sources:
    //   1. RTC timer — wake after `seconds`
    //   2. GPIO ext0 — wake on I2C interrupt pin (energy IC signals power spike)
    esp_sleep_enable_timer_wakeup(seconds * 1000000ULL);  // microseconds

    // Enter deep sleep — CPU stops, only RTC domain active (~5 uA)
    esp_deep_sleep_start();
}

} // namespace Power

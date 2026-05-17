/**
 * Power Manager — Bare-metal control of energy harvesting ICs.
 *
 * Owns:
 *   - I2C communication with AEM10941 / BQ25570
 *   - GPIO wake/sleep control
 *   - Watchdog timer feeding
 *   - Ultra-low-power sleep cycle management
 *
 * NOTE: This is C++ bare-metal code. No dynamic allocation. All buffers
 * are fixed-size. Every register write is documented with a comment.
 */

#ifndef POWER_MANAGER_H
#define POWER_MANAGER_H

#include <stdint.h>

namespace Power {

// I2C device addresses (7-bit)
constexpr uint8_t AEM10941_ADDR = 0x48;  // e-peas ambient energy manager
constexpr uint8_t BQ25570_ADDR  = 0x10;  // TI nano-power boost charger

// I2C bus (ESP32-S3 default: Wire / Wire1)
constexpr uint8_t I2C_SDA = 8;   // GPIO8 — SDA pin
constexpr uint8_t I2C_SCL = 9;   // GPIO9 — SCL pin

// Power mode thresholds (harvested milliwatts)
constexpr float THRESH_FULL       = 500.0f;
constexpr float THRESH_REDUCED    = 100.0f;
constexpr float THRESH_LOW_POWER  = 10.0f;

enum class Mode : uint8_t {
    FULL        = 0,  // >500 mW — everything on
    REDUCED     = 1,  // 100-500 mW — reduce TX power, disable non-essential
    LOW_POWER   = 2,  // 10-100 mW — intermittent beacon only
    SLEEP       = 3,  // <10 mW — wake on interrupt, maintain mesh registration
};

/**
 * Initialize the power subsystem.
 *   1. Start I2C bus at 100 kHz (standard mode — reliable over longer wires)
 *   2. Probe for AEM10941, then BQ25570 fallback
 *   3. Configure energy IC for optimal MPPT (Maximum Power Point Tracking)
 *   4. Read initial harvested power and set initial mode
 */
bool init();

/**
 * Read harvested power from the energy management IC.
 * AEM10941: reads 12-bit ADC from registers 0x00 (high) + 0x01 (low)
 * BQ25570: reads 8-bit ADC from register 0x02
 * Returns power in milliwatts. Returns 0.0 if hardware unavailable.
 */
float readHarvestedPower_mW();

/**
 * Read storage capacitor / battery voltage.
 * AEM10941: reads 12-bit ADC from registers 0x02 (high) + 0x03 (low)
 * Returns voltage in Volts. Returns -1.0 if hardware unavailable.
 */
float readBatteryVoltage_V();

/**
 * Determine power mode from harvested milliwatts.
 */
Mode getModeFromPower(float harvested_mw);

/**
 * Get the current power mode as a human-readable string.
 */
const char* modeToString(Mode mode);

/**
 * Apply power mode to hardware.
 *   - FULL:      enable radio, enable mesh beacon, max TX power
 *   - REDUCED:   reduce TX power by 50%, disable LED
 *   - LOW_POWER: beacon every 30s, no routing, no gateway
 *   - SLEEP:     deep sleep, wake on GPIO interrupt or timer
 */
void applyMode(Mode mode);

/**
 * Feed the hardware watchdog timer.
 * Must be called at least every 2 seconds or the system resets.
 * Register write: WDTCSR = (1<<WDCE)|(1<<WDE) — unlocks watchdog config
 * Then: WDTCSR = (1<<WDE)|(1<<WDP2) — sets 2-second timeout
 */
void feedWatchdog();

/**
 * Enter deep sleep for a specified number of seconds.
 * GPIO wake sources: I2C interrupt from energy IC (harvested power spike)
 * Timer wake source: RTC timer alarm
 * Before sleep: save mesh state to RTC memory, flush serial buffer
 */
void deepSleep(uint32_t seconds);

} // namespace Power

#endif // POWER_MANAGER_H

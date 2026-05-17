/**
 * Radio Manager — Bare-metal TVWS radio control.
 *
 * Owns:
 *   - TVWS radio module initialization (SPI or UART)
 *   - Spectrum scanning for unoccupied UHF channels
 *   - Channel selection and connection management
 *   - RSSI / SNR reporting
 *
 * In production, this interfaces with TVWS hardware like:
 *   - Adaptrum ACRS2 (UART)
 *   - 6Harmonics GWS series (SPI)
 *
 * In development, returns simulated channel data.
 */

#ifndef RADIO_MANAGER_H
#define RADIO_MANAGER_H

#include <stdint.h>

namespace Radio {

// TVWS band limits (MHz) — US FCC Part 15
constexpr float MIN_FREQ_MHZ = 470.0f;
constexpr float MAX_FREQ_MHZ = 698.0f;
constexpr float CHANNEL_BW_MHZ = 6.0f;

// Maximum allowed EIRP per FCC (dBm)
constexpr float MAX_TX_POWER_DBM = 36.0f;

struct Channel {
    float frequency_mhz;
    float bandwidth_mhz;
    float power_dbm;
    bool occupied;
    float snr_db;
};

struct LinkStatus {
    bool connected;
    float rssi_dbm;
    float snr_db;
    float throughput_mbps;
    float frequency_mhz;
};

/**
 * Initialize the radio hardware.
 * In production: opens UART to TVWS module, performs self-test.
 * In dev: sets up simulation state.
 */
bool init();

/**
 * Scan available TVWS channels.
 * In production: queries FCC spectrum database + local spectrum sensing.
 * In dev: returns simulated channels with some marked occupied.
 */
uint8_t scanChannels(Channel* out_channels, uint8_t max_channels);

/**
 * Select the best available channel (highest SNR, not occupied).
 */
bool selectBestChannel(Channel& out_channel);

/**
 * Connect to a TVWS channel for backhaul.
 */
bool connect(const Channel& channel);

/**
 * Disconnect from the current channel.
 */
void disconnect();

/**
 * Get current link quality.
 */
LinkStatus getLinkStatus();

/**
 * Check if currently connected to a backhaul channel.
 */
bool isConnected();

} // namespace Radio

#endif // RADIO_MANAGER_H

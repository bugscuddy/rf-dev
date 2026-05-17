#include "radio_manager.h"
#include <Arduino.h>

namespace Radio {

// Simulation state (used when no hardware is present)
static bool g_connected = false;
static Channel g_active_channel = {0, 0, 0, true, 0};

bool init() {
    // In production:
    //   Serial2.begin(115200, SERIAL_8N1, RADIO_RX_PIN, RADIO_TX_PIN);
    //   sendCommand("AT+INIT");
    //   return waitForOK(5000);
    
    g_connected = false;
    return true;
}

uint8_t scanChannels(Channel* out_channels, uint8_t max_channels) {
    // In production:
    //   sendCommand("AT+SCAN");
    //   parse multi-line response into Channel array
    
    // Simulation: generate channels across TVWS band
    uint8_t count = 0;
    for (float freq = MIN_FREQ_MHZ; freq < MAX_FREQ_MHZ && count < max_channels; freq += CHANNEL_BW_MHZ) {
        // Mark every 6th channel as occupied (simulating licensed broadcast)
        bool occupied = ((int)freq % 36 == 0);
        out_channels[count] = {
            freq,
            CHANNEL_BW_MHZ,
            occupied ? 0.0f : MAX_TX_POWER_DBM,
            occupied,
            occupied ? 0.0f : (20.0f + random(15))
        };
        count++;
    }
    return count;
}

bool selectBestChannel(Channel& out_channel) {
    Channel channels[40];
    uint8_t count = scanChannels(channels, 40);
    if (count == 0) return false;

    // Find channel with highest SNR that is not occupied
    float best_snr = -100.0f;
    int best_idx = -1;
    for (int i = 0; i < count; i++) {
        if (!channels[i].occupied && channels[i].snr_db > best_snr) {
            best_snr = channels[i].snr_db;
            best_idx = i;
        }
    }

    if (best_idx < 0) return false;
    out_channel = channels[best_idx];
    return true;
}

bool connect(const Channel& channel) {
    if (channel.occupied) return false;

    // In production:
    //   char cmd[64];
    //   snprintf(cmd, sizeof(cmd), "AT+FREQ=%.1f", channel.frequency_mhz);
    //   sendCommand(cmd);
    //   sendCommand("AT+CONNECT");

    g_active_channel = channel;
    g_connected = true;
    return true;
}

void disconnect() {
    // In production: sendCommand("AT+DISCONNECT");
    g_connected = false;
    g_active_channel = {0, 0, 0, true, 0};
}

LinkStatus getLinkStatus() {
    if (!g_connected) {
        return {false, -100.0f, 0.0f, 0.0f, 0.0f};
    }

    // In production: query radio module registers
    // Simulation: return plausible values
    return {
        true,
        -65.0f + random(-10, 10),  // RSSI varies slightly
        g_active_channel.snr_db,
        g_active_channel.bandwidth_mhz * 2.5f,  // rough throughput estimate
        g_active_channel.frequency_mhz,
    };
}

bool isConnected() {
    return g_connected;
}

} // namespace Radio

#pragma once

// Wi-Fi bring-up tuned for a device that deep-sleeps between uses.
//
// Deep sleep wipes the Wi-Fi stack, so a naive reconnect pays for a full
// channel scan plus DHCP on every wake. This module remembers the access
// point's channel and BSSID across sleeps (in RTC memory) and uses a static IP
// (from secrets.h), which together bring a wake-to-connected time down from
// seconds to a few hundred milliseconds.
namespace wifi_connection
{
    // Connects to WIFI_SSID. Tries the remembered channel/BSSID first and
    // falls back to a full scan if that fails (e.g. the router changed
    // channel). Blocks for at most ~2x the connect timeout. Returns true if
    // connected.
    bool connect();
} // namespace wifi_connection

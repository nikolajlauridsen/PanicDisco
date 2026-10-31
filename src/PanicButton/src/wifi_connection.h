#pragma once

/**
 * Wi-Fi bring-up tuned for a device that deep-sleeps between uses.
 *
 * Deep sleep wipes the Wi-Fi stack, so a naive reconnect pays for a full
 * channel scan plus DHCP on every wake. This module remembers the access
 * point's channel and BSSID across sleeps (in RTC memory) and uses a static IP
 * (from secrets.h), which together bring a wake-to-connected time down from
 * seconds to a few hundred milliseconds.
 *
 * Nothing that opens a socket (DiscoClient, HTTPClient) may run before
 * connect() has succeeded: the TCP/IP stack is only initialised by it, and
 * using it beforehand aborts the firmware rather than returning an error.
 */
namespace wifi_connection
{
    /**
     * Connects to WIFI_SSID. Tries the remembered channel/BSSID first and
     * falls back to a full scan if that fails (e.g. the router changed
     * channel). Blocks for at most ~2x the connect timeout.
     *
     * @return true if connected.
     */
    bool connect();

    /**
     * @return true if the station link is currently up. Cheap; use it to skip
     *         connect() when a previous caller already connected this wake.
     */
    bool isConnected();
} // namespace wifi_connection

#include "wifi_connection.h"

#include <Arduino.h>
#include <WiFi.h>
#include <cstring>

#include "log.h"
#include "secrets.h"

namespace
{
    constexpr uint32_t CONNECT_TIMEOUT_MS = 5000;
    constexpr size_t BSSID_LEN = 6;

    // RTC_DATA_ATTR places these in RTC slow memory, which survives deep sleep
    // (but not a power cycle or reset button - they start zeroed then).
    RTC_DATA_ATTR uint8_t savedChannel = 0;
    RTC_DATA_ATTR uint8_t savedBssid[BSSID_LEN];

    bool attempt(bool useSavedAccessPoint)
    {
        WiFi.mode(WIFI_STA);
        WiFi.setSleep(false); // We deep sleep between uses, so no modem power-save needed while awake
        WiFi.setHostname("PanicButton");

        // Static IP: skips DHCP negotiation, which is a measurable part of the connect time.
        WiFi.config(IPAddress(STATIC_IP), IPAddress(GATEWAY_IP), IPAddress(SUBNET_MASK), IPAddress(DNS_IP));

        if (useSavedAccessPoint)
        {
            // Skips the channel scan entirely - needs the channel/BSSID to still be valid.
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD, savedChannel, savedBssid);
        }
        else
        {
            WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
        }
        return WiFi.waitForConnectResult(CONNECT_TIMEOUT_MS) == WL_CONNECTED;
    }
} // namespace

namespace wifi_connection
{
    bool connect()
    {
        const uint32_t t0 = millis();
        const bool ok = (savedChannel != 0 && attempt(true)) || attempt(false);

        if (ok)
        {
            savedChannel = WiFi.channel();
            std::memcpy(savedBssid, WiFi.BSSID(), BSSID_LEN);
        }

        LOG("WiFi %s in %lu ms\n", ok ? "connected" : "FAILED", millis() - t0);
        if (ok)
        {
            LOG("IP %s\n", WiFi.localIP().toString().c_str());
        }
        return ok;
    }
} // namespace wifi_connection

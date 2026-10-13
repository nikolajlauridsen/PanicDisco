#include <Arduino.h>
#include <WiFi.h>
#include "secrets.h"  // WIFI_SSID / WIFI_PASSWORD - gitignored, see include/secrets.example.h
/*
NOTE:
======
Bit mask of GPIO numbers which will cause wakeup. Only GPIOs
which have RTC functionality can be used in this bit map.
For different SoCs, the related GPIOs are:
- ESP32: 0, 2, 4, 12-15, 25-27, 32-39
- ESP32-S2: 0-21
- ESP32-S3: 0-21
- ESP32-C6: 0-7
- ESP32-H2: 7-14
*/
#define BUTTON_PIN_BITMASK (1ULL << GPIO_NUM_0)

static constexpr gpio_num_t BUTTON_PIN = GPIO_NUM_0;

RTC_DATA_ATTR uint8_t savedChannel = 0;
RTC_DATA_ATTR uint8_t savedBssid[6];
bool connect(bool fast){
    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false); // We deep sleep, so no need for wifi sleep
    WiFi.setHostname("PanicButton");
    
    // Allows us to skip DHCP negotion, speeding up connection.
    WiFi.config(
        IPAddress(192, 168, 1, 12), // Your local IP (pin this in your router)
        IPAddress(192, 168, 1, 1), // Gateway (router IP)
        IPAddress(255, 255, 255, 0), // Subnet nask,
        IPAddress(192, 168, 1, 1)); // DNS (your router)
    
    // Skips wifi channel scan, but needs valid channel and bssid.    
    if(fast){
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD, savedChannel, savedBssid);
    }
    else {
        WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    }
    return WiFi.waitForConnectResult(5000) == WL_CONNECTED;
}

void configure_wifi()
{
    uint32_t t0 = millis();
    bool ok = (savedChannel != 0 && connect(true)) || connect(false);

    if(ok){
        savedChannel = WiFi.channel();
        memcpy(savedBssid, WiFi.BSSID(), 6);
    }

    Serial.printf("WiFi %s in %lu ms\n", ok ? "connected" : "FAILED", millis() - t0);
    Serial.println(WiFi.localIP());
}

RTC_DATA_ATTR int bootCount = 0;
void setup()
{
    Serial.begin(115200);
    delay(100);
    delay(3000);

    ++bootCount;
    Serial.println("Boot number: " + String(bootCount));

    configure_wifi();

    esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK, ESP_EXT1_WAKEUP_ANY_HIGH);
    Serial.println("Going to sleep now");
    esp_deep_sleep_start();
}

void loop()
{
}

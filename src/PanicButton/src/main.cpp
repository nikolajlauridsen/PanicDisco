#include <Arduino.h>
#include <WiFi.h>
#include "secrets.h"  // WIFI_SSID / WIFI_PASSWORD - gitignored, see include/secrets.example.h

// The XIAO ESP32C6's user LED (GPIO 15) is active low:
// LOW turns it on, HIGH turns it off.

// uint32_t: the "_t" suffix means "type" - a typedef from <stdint.h>, not a
// built-in keyword. Fixed-width types guarantee exactly 32 bits on any platform,
// unlike plain int/long whose size varies.
static constexpr uint32_t BLINK_INTERVAL_MS = 500;

void configure_wifi()
{
    WiFi.mode(WIFI_STA);
    WiFi.setHostname("PanicButton");
    WiFi.setSleep(WIFI_PS_MAX_MODEM);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Connecting to ");
    Serial.print(WIFI_SSID);
    Serial.print(" .");
    while (WiFi.status() != WL_CONNECTED) {
        Serial.print('.');
        delay(1000);
    }

    Serial.println("\nConnected!");
    Serial.println(WiFi.localIP());
}

void setup()
{
    Serial.begin(115200);
    delay(100);
    configure_wifi();
}

void loop()
{
    Serial.println("Hello world");
    delay(1000);
}

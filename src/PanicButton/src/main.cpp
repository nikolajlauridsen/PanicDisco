#include <Arduino.h>

#include "disco_client.h"
#include "secrets.h" // WIFI_*, STATIC_IP, API_BASE_URL - gitignored, see include/secrets.example.h
#include "wifi_connection.h"

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
static constexpr gpio_num_t BUTTON_PIN = GPIO_NUM_0;
#define BUTTON_PIN_BITMASK (1ULL << BUTTON_PIN)

RTC_DATA_ATTR bool panicMode = false;

static DiscoClient disco(API_BASE_URL);

void handlePanicbutton()
{
    if (wifi_connection::connect() == false)
    {
        Serial.printf("Couldn't connect :( skipping")
    }

    if (panicMode == false)
    {
        const int status = disco.panicStart();
        Serial.printf("POST /panic/start -> %d\n", status);
        if (status == 200)
        {
            panicMode = true;
        }
    }
    else
    {
        const int status = disco.panicStop();
        Serial.printf("POST /panic/stop -> %d\n", status);
        if (status == 200)
        {
            panicMode = false;
        }
    }
}

void setup()
{
    const uint32_t t0 = millis();
    Serial.begin(115200);
    delay(100);
    delay(3000);

    handlePanicbutton();

    const uint32_t t_final = millis() - t0 - 3000;
    Serial.printf("Total in setup: %lu ms\n", t_final);

    esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK, ESP_EXT1_WAKEUP_ANY_HIGH);
    Serial.println("Going to sleep now");
    Serial.flush();
    esp_deep_sleep_start();
}

void loop()
{
}

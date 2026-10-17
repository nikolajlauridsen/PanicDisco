#include <Arduino.h>
#include <driver/rtc_io.h>

#include "disco_client.h"
#include "log.h"
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
static constexpr gpio_num_t PANIC_BUTTON_PIN = GPIO_NUM_0;
static constexpr gpio_num_t REED_PIN = GPIO_NUM_1;
#define BUTTON_PIN_BITMASK (1ULL << PANIC_BUTTON_PIN)
#define REED_PIN_BITMASK (1ULL << REED_PIN)

static DiscoClient disco(API_BASE_URL);

void handlePanicbutton()
{
    if (wifi_connection::connect() == false)
    {
        LOG("Couldn't connect :( skipping\n");
    }
    // Re-enable button pin so we can read
    pinMode(PANIC_BUTTON_PIN, INPUT);
    
    const int status = disco.panicStart();
    LOG("POST /panic/start -> %d\n", status);
    if(status != 200){
        LOG("Panic failed, exiting...\n");
        return;
    }

    while(digitalRead(PANIC_BUTTON_PIN) == HIGH)
    {
        // The button is held high untill it's undone by twisting, so we'll play as long as it's high.
        // Small delay, just to be nice
        delay(100);
    }

    // We should do our absolute best effort to stop the disco again
    uint8_t maxTries = 10;
    for(int tries = 0; tries < maxTries; tries++)
    {
        const int stopStatus = disco.panicStop();
        LOG("POST /panic/stop -> %d\n", stopStatus);
        if(stopStatus == 200)
        {
            break;
        }
        LOG("Stop failed %d/%d tries.\n", tries+1, maxTries);
        delay(100*tries);
    }
}

void handleLidOpened()
{
    while (digitalRead(REED_PIN) == HIGH)
    {
        LOG("Lid open...\n");
        delay(500);
    }
}

void enterSleep()
{
    digitalWrite(LED_BUILTIN, HIGH);
    esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK | REED_PIN_BITMASK, ESP_EXT1_WAKEUP_ANY_HIGH);
    LOG("Going to sleep now\n");
    LOG_FLUSH();
    esp_deep_sleep_start();
}

void setup()
{
    // For debugging purposes let's enable our LED
    // Weirdly for the builtin LED low = on
    pinMode(LED_BUILTIN, OUTPUT);
    digitalWrite(LED_BUILTIN, LOW);
    LOG_BEGIN(); // no-op in the release build; opens the port and waits for USB enumeration in debug
    const uint32_t t0 = millis();
    // Re-arm the reed pin.
    rtc_gpio_deinit(REED_PIN);
    pinMode(REED_PIN, INPUT);

    // The reed switch is static high when the lid is open, so it's an easy way to determine what path to take
    int reedValue = digitalRead(REED_PIN);
    if (reedValue == HIGH)
    {
        handleLidOpened();
    }
    else
    {
        handlePanicbutton();
    }

    LOG("Total in setup: %lu ms\n", millis() - t0);

    enterSleep();
}

void loop()
{
}

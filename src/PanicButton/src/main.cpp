#include <Arduino.h>
#include <driver/rtc_io.h>

#include "disco_client.h"
#include "log.h"
#include "menu.h"
#include "pinout.h"
#include "secrets.h" // WIFI_*, STATIC_IP, API_BASE_URL - gitignored, see include/secrets.example.h
#include "wifi_connection.h"

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
    if (status != 200)
    {
        LOG("Panic failed, exiting...\n");
        return;
    }

    while (digitalRead(PANIC_BUTTON_PIN) == HIGH)
    {
        // The button is held high untill it's undone by twisting, so we'll play as long as it's high.
        // Small delay, just to be nice
        delay(100);
    }

    // We should do our absolute best effort to stop the disco again
    uint8_t maxTries = 10;
    for (int tries = 0; tries < maxTries; tries++)
    {
        const int stopStatus = disco.panicStop();
        LOG("POST /panic/stop -> %d\n", stopStatus);
        if (stopStatus == 200)
        {
            break;
        }
        LOG("Stop failed %d/%d tries.\n", tries + 1, maxTries);
        delay(100 * tries);
    }
}

void handleLidOpened()
{
    menu::initializeControls();
    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = menu::readControls();

        switch (controlsValue)
        {
        case menu::RIGHT:
            LOG("Moving right...\n");
            break;
        case menu::LEFT:
            LOG("Moving left...\n");
            break;
        case menu::ENTER:
            LOG("Enter pushed...\n");
            break;
        case menu::BACK:
            LOG("Back pushed...\n");
            break;
        }
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
    // If not waking from the pin wakeups we just exit immediately
    if (esp_sleep_get_wakeup_cause() != ESP_SLEEP_WAKEUP_EXT1)
    {
        enterSleep();
    }

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

#include <Arduino.h>

#include <driver/rtc_io.h>

#include "action_menu.h"
#include "controls.h"
#include "disco_client.h"
#include "display.h"
#include "log.h"
#include "pinout.h"
#include "secrets.h" // WIFI_*, STATIC_IP, API_BASE_URL - gitignored, see include/secrets.example.h
#include "volume_menu_item.h"
#include "wifi_connection.h"
#include "label_menu_item.h"

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
    controls::begin();
    display::begin();
    static VolumeMenuItem volumeItem;
    static LabelMenuItem demo1("Demo 1");
    static LabelMenuItem demo2("Demo 2");
    static LabelMenuItem demo3("Demo 3");
    static LabelMenuItem demo4("Demo 4");
    static LabelMenuItem demo5("Demo 5");
    static ActionMenuItem* const menuItems[] = {&volumeItem, &demo1, &demo2, &demo3, &demo4, &demo5};
    static ActionMenu menu(menuItems);

    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue)
        {
        case controls::RIGHT:
            menu.moveNext();
            break;
        case controls::LEFT:
            menu.movePrevious();
            break;
        case controls::ENTER:
            menu.select();
            break;
        }

        // Always clear the screen when returning from a menu.
        display::clear();
    }

    display::clear();
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

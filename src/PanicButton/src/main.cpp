#include <Arduino.h>

#include <driver/rtc_io.h>

#include "controls.h"
#include "disco_client.h"
#include "display.h"
#include "log.h"
#include "menu/action_menu.h"
#include "menu/items/select_track_menu_item.h"
#include "menu/items/volume_menu_item.h"
#include "pinout.h"
#include "secrets.h" // WIFI_*, STATIC_IP, API_BASE_URL - gitignored, see include/secrets.example.h
#include "wifi_connection.h"

/** The one server client, shared by the panic path and the menu items. */
static DiscoClient disco(API_BASE_URL);

/**
 * Wake path when the lid is closed: the panic button was twisted on.
 *
 * Connects, fires POST /panic/start, then waits while the button stays
 * latched HIGH. Once it's twisted back off, POST /panic/stop is retried up to
 * ten times with growing back-off, since leaving the disco running is the
 * worst outcome. Returns to setup(), which deep-sleeps.
 */
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

/**
 * Wake path when the lid is open: drives the OLED menu until it closes.
 *
 * Builds the menu once (static items and array, because ActionMenu holds a
 * non-owning span over them) and loops on controls::read(): LEFT/RIGHT move
 * the cursor, ENTER hands the screen to the selected item until it returns.
 * The reed switch going LOW ends the loop. Returns to setup(), which
 * deep-sleeps.
 */
void handleLidOpened()
{
    controls::begin();
    display::begin();
    static SelectTrackMenuItem trackMenuItem(disco);
    static VolumeMenuItem volumeItem;
    static ActionMenuItem* const menuItems[] = {&trackMenuItem, &volumeItem};
    static ActionMenu menu(menuItems);

    display::renderMenu(&menu);

    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue)
        {
        case controls::RIGHT:
            LOG("Moving right");
            menu.moveNext();
            display::renderMenu(&menu);
            break;
        case controls::LEFT:
            LOG("Moving left");
            menu.movePrevious();
            display::renderMenu(&menu);
            break;
        case controls::ENTER:
            display::clear();
            menu.select();
            display::setFont(FONT_SMALL);
            display::renderMenu(&menu);
            break;
        }
    }

    display::clear();
}

/**
 * Turns the LED off, arms ext1 wake on the panic button or the reed switch
 * going HIGH, and enters deep sleep. Never returns; the next wake starts
 * again at setup().
 */
void enterSleep()
{
    digitalWrite(LED_BUILTIN, HIGH);
    esp_sleep_enable_ext1_wakeup(BUTTON_PIN_BITMASK | REED_PIN_BITMASK, ESP_EXT1_WAKEUP_ANY_HIGH);
    LOG("Going to sleep now\n");
    LOG_FLUSH();
    esp_deep_sleep_start();
}

/**
 * Entry point on every wake. Decides which path to take from the reed switch
 * (HIGH = lid open = menu, LOW = lid closed = panic button), runs it, then
 * deep-sleeps. A wake that isn't from ext1 (e.g. first power-on or a reset)
 * goes straight back to sleep so the device only ever acts on the two inputs.
 */
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

/** Never reached: setup() always ends in deep sleep. */
void loop()
{
}

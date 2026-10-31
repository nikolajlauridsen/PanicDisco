#pragma once

#include <Arduino.h>

/**
 * Every GPIO the firmware uses, in one place. Never inline a pin number
 * elsewhere; add it here and refer to it by name.
 *
 * The two wake sources (panic button, reed switch) must be on RTC-capable
 * pins, because they're used in the ext1 deep-sleep wake mask. On the
 * ESP32-C6 that means GPIO 0-7. (Other SoCs for reference: ESP32 0, 2, 4,
 * 12-15, 25-27, 32-39; ESP32-S2/S3 0-21; ESP32-H2 7-14.) The remaining pins
 * are only read while awake and can be anything.
 */

/** The panic button. Latches HIGH while twisted on; a wake source. */
static constexpr gpio_num_t PANIC_BUTTON_PIN = GPIO_NUM_0;

/** Reed switch on the lid. HIGH while the lid is open; a wake source. */
static constexpr gpio_num_t REED_PIN = GPIO_NUM_1;

/** KY-040 rotary encoder, channel A (CLK). */
static constexpr gpio_num_t PIN_A = GPIO_NUM_19;

/** KY-040 rotary encoder, channel B (DT). */
static constexpr gpio_num_t PIN_B = GPIO_NUM_17;

/** Back button: to 3V3 with an external pull-down, so pressed = HIGH. */
static constexpr gpio_num_t BACK_BUTTON_PIN = GPIO_NUM_20;

/** KY-040's built-in push switch (SW): to GND with a pull-up, pressed = LOW. */
static constexpr gpio_num_t ENTER_BUTTON_PIN = GPIO_NUM_18;

/** ext1 wake mask bit for the panic button. */
#define BUTTON_PIN_BITMASK (1ULL << PANIC_BUTTON_PIN)

/** ext1 wake mask bit for the reed switch. */
#define REED_PIN_BITMASK (1ULL << REED_PIN)

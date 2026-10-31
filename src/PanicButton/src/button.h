#pragma once

#include <Arduino.h>

/**
 * A debounced momentary push button on one GPIO.
 *
 * Reports each press exactly once, on the transition into the pressed state.
 * Mechanical contacts bounce for a few ms on each press and release, so
 * transitions closer together than the debounce time are ignored. Polling
 * based: call justPressed() from a loop, there are no interrupts involved.
 *
 * Usage:
 *   Button enter(GPIO_NUM_18, LOW);   // pressed = pin reads LOW
 *   enter.begin(INPUT_PULLUP);        // or begin() if the pull resistor is external
 *   if (enter.justPressed()) { ... }
 */
class Button
{
  public:
    /**
     * @param pin          the GPIO the button is wired to.
     * @param pressedLevel the level the pin reads while held down - LOW for a
     *                     button to GND with a pull-up, HIGH for a button to
     *                     3V3 with a pull-down.
     */
    explicit Button(gpio_num_t pin, int pressedLevel);

    /**
     * Configures the pin and samples its current level, so a button already
     * held at startup doesn't count as a press.
     *
     * @param pullMode passed to pinMode: INPUT when the pull resistor is on
     *                 the board, INPUT_PULLUP/INPUT_PULLDOWN to use the chip's
     *                 internal one.
     */
    void begin(uint8_t pullMode = INPUT);

    /**
     * Changes how long the pin must hold a new level before it counts as a
     * real transition. Default is 25 ms.
     */
    void setDebounce(uint32_t debounceMs);

    /**
     * @return true once per press, on the transition into the pressed state;
     *         false while held, released, or bouncing.
     */
    bool justPressed();

  private:
    gpio_num_t pin;
    int pressedLevel;
    uint32_t debounceMs = 25;
    bool wasPressed = false;
    uint32_t lastChange = 0;
};

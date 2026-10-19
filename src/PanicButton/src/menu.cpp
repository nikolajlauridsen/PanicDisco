#include "menu.h"

#include <Arduino.h>

#include "button.h"
#include "pinout.h"

namespace
{
    // How the KY-040 rotary encoder works
    // ===================================
    // Pins A and B are two switches that open and close slightly out of phase
    // as the knob turns. Read together they give one of four combinations.
    // We pack them into a single 2-bit number, A first then B, so e.g. 0b10
    // means A is HIGH and B is LOW.
    //
    // Turning the knob one click (from one detent to the next) walks through
    // all four combinations and ends up back where it started:
    //
    //   one direction:   AB = 11 -> 01 -> 00 -> 10 -> 11
    //   the other way:   AB = 11 -> 10 -> 00 -> 01 -> 11
    //
    // Each move to a neighbouring combination is a "quarter step". Four quarter
    // steps the same way is one click. A bouncing contact looks like a quarter
    // step immediately followed by the reverse quarter step, so the two cancel
    // out and no click is reported. That is what makes this immune to bounce
    // without any timing-based debounce.

    constexpr uint8_t AT_DETENT = 0b11; // Both pins HIGH: the knob is resting on a click

    // Direction of a quarter step, looked up as QUARTER_STEP[previous][current].
    // +1 is one way round, -1 the other. 0 means either no change, or both pins
    // changed at the same time, which a real turn can never do, so it's noise.
    const int8_t QUARTER_STEP[4][4] = {
        // to:  00  01  10  11       from:
        {0, -1, 1, 0}, // 00
        {1, 0, 0, -1}, // 01
        {-1, 0, 0, 1}, // 10
        {0, 1, -1, 0}, // 11
    };

    uint8_t encoderState = AT_DETENT;
    int8_t quarterSteps = 0; // Net quarter steps since the knob last rested on a detent

    // Pack the two pins into one 2-bit number: A becomes bit 1, B becomes bit 0.
    uint8_t readEncoderState()
    {
        // digitalRead returns exactly 0 or 1 on this core, so the bits pack directly.
        return (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
    }

    /**
     * Reads one step of the rotary encoder.
     *
     * Tracks the pins through the four-combination cycle described above and
     * only reports a step once the knob has come to rest on the next detent.
     *
     * @return menu::LEFT for a step counter-clockwise,
     *         menu::RIGHT for a step clockwise,
     *         menu::NoOp if the encoder has not moved since the last call.
     */
    menu::Control readEncoder()
    {
        const uint8_t previous = encoderState;
        const uint8_t current = readEncoderState();
        if (current == previous)
        {
            return menu::NOOP;
        }

        quarterSteps += QUARTER_STEP[previous][current];
        encoderState = current;

        // Only judge the movement once the knob is resting on a detent again.
        if (current != AT_DETENT)
        {
            return menu::NOOP;
        }

        const int8_t steps = quarterSteps;
        quarterSteps = 0;

        if (steps >= 4)
        {
            return menu::RIGHT;
        }
        if (steps <= -4)
        {
            return menu::LEFT;
        }
        return menu::NOOP; // Wiggled part way and came back: not a click
    }

    // Enter is the KY-040's built-in push switch: shorts to GND when pressed,
    // external pull-up on the board. Back is a plain button to 3V3 with an
    // external pull-down. Both pull resistors are on the board, hence begin()
    // with the default INPUT mode.
    Button enterButton(ENTER_BUTTON_PIN, LOW);
    Button backButton(BACK_BUTTON_PIN, HIGH);

    menu::Control readButtons()
    {
        // Update both every call so a held button's release is always tracked,
        // even when the other button's press is what gets reported.
        const bool enterJustPressed = enterButton.justPressed();
        const bool backJustPressed = backButton.justPressed();

        if (enterJustPressed)
        {
            return menu::ENTER;
        }
        if (backJustPressed)
        {
            return menu::BACK;
        }
        return menu::NOOP;
    }
} // namespace

namespace menu
{
    Control readControls()
    {
        Control readValue = readEncoder();
        if (readValue != NOOP)
        {
            return readValue;
        }

        return readButtons();
    }

    void initializeControls()
    {
        // Initialize encoder
        pinMode(PIN_A, INPUT);
        pinMode(PIN_B, INPUT);
        encoderState = readEncoderState();
        quarterSteps = 0;

        // Initialize buttons
        enterButton.begin();
        backButton.begin();
    }
} // namespace menu

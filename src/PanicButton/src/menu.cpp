#include <Arduino.h>
#include "menu.h"
#include "pinout.h"

namespace
{
    // Valid quadrature transitions: index is (previous state << 2) | current state,
    // each state being (A << 1) | B. +1/-1 for a legal quarter step, 0 for no
    // change or an illegal jump (both pins changed at once = contact noise).
    const int8_t QUADRATURE_TABLE[16] = {
        0,  -1, 1,  0, //
        1,  0,  0,  -1, //
        -1, 0,  0,  1, //
        0,  1,  -1, 0, //
    };

    uint8_t encoderState = 0b11; // KY-040 rests with both pins HIGH at a detent
    int8_t quarterSteps = 0;

    uint8_t readEncoderState()
    {
        return (digitalRead(PIN_A) << 1) | digitalRead(PIN_B);
    }

    /**
     * Reads one step of the rotary encoder.
     *
     * Decodes both pins as a Gray code state machine and only reports a step once
     * a full cycle has completed back at a detent. Contact bounce shows up as a
     * quarter step forward and back that cancel out, so no time-based debounce
     * is needed.
     *
     * @return menu::LEFT for a step counter-clockwise,
     *         menu::RIGHT for a step clockwise,
     *         menu::NoOp if the encoder has not moved since the last call.
     */
    menu::Control readEncoder()
    {
        const uint8_t state = readEncoderState();
        if (state == encoderState)
        {
            return menu::NoOp;
        }
        quarterSteps += QUADRATURE_TABLE[(encoderState << 2) | state];
        encoderState = state;

        // A detent is reached when both pins are HIGH again. Only then do we know
        // whether the accumulated quarter steps add up to a real click.
        if (state != 0b11)
        {
            return menu::NoOp;
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
        return menu::NoOp; // bounced partway and came back, not a click
    }
} // namespace

namespace menu
{
    Control readControls()
    {
        return readEncoder();
    }

    void initializeControls()
    {
        // Initialize encoder
        pinMode(PIN_A, INPUT);
        pinMode(PIN_B, INPUT);
        // Read initial position
        encoderState = readEncoderState();
        quarterSteps = 0;

        // Initialize buttons
    }
} // namespace menu

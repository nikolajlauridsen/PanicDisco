#pragma once

/**
 * The user input on the lid: a KY-040 rotary encoder with its built-in push
 * switch (ENTER) and a separate back button.
 *
 * All three are folded into one Control value per read() so callers only
 * deal with "what did the user just do", not with pins. Polling based, no
 * interrupts: call read() repeatedly from a loop. The encoder is decoded
 * with a Gray-code quadrature table where one click is a full four-step
 * cycle, which makes it immune to contact bounce without any timing-based
 * debounce (see controls.cpp). Pin numbers live in pinout.h.
 */
namespace controls
{
    /**
     * One user action. LEFT/RIGHT are encoder clicks (counter-clockwise /
     * clockwise), ENTER and BACK are button presses, NOOP means nothing
     * happened since the last read(). LEFT/RIGHT are -1/+1 so they can be
     * used directly as a cursor delta.
     */
    enum Control
    {
        LEFT = -1,
        RIGHT = 1,
        ENTER = 2,
        BACK = 3,
        NOOP = 0,
    };

    /**
     * Polls the encoder and both buttons once.
     *
     * Reports at most one action per call: an encoder click takes priority
     * over a button press, and ENTER over BACK. Button presses are reported
     * once per press (on the press edge, debounced), not while held.
     *
     * @return the action since the last call, or NOOP.
     */
    Control read();

    /**
     * Configures the encoder and button pins and reads the encoder's resting
     * state. Call once before read(). All pull resistors are on the boards,
     * so pins are plain INPUT.
     */
    void begin();
}

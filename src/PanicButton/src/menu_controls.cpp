#include "pinout.h"
#include <Arduino.h>


namespace
{
    int pinALast;
    int aVal;
    /**
     * Reads one step of the rotary encoder.
     *
     * @return -1 for a step left (counter-clockwise),
     *          1 for a step right (clockwise),
     *          0 if the encoder has not moved since the last call.
     */
    int readEncoder()
    {
        static uint32_t lastChange = 0;
        aVal = digitalRead(PIN_A);

        if (aVal == pinALast)
        {
            return 0;
        }
        pinALast = aVal;

        if (aVal != LOW)
        {
            return 0;
        }

        // Contact bounce shows up as extra edges within a few ms.
        const uint32_t now = millis();
        if (now - lastChange < 5)
        {
            return 0;
        }
        lastChange = now;

        return digitalRead(PIN_B) != aVal ? 1 : -1;
    }
} // namespace

namespace menu_controls
{
    int readMenuControls()
    {
        return readEncoder();
    }

    void initializeEncoder()
    {
        pinMode(PIN_A, INPUT);
        pinMode(PIN_B, INPUT);
        // Read initial positon
        pinALast = digitalRead(PIN_A);
    }
} // namespace menu_controls
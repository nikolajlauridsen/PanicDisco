#include "button.h"

Button::Button(gpio_num_t pin, int pressedLevel) : pin(pin), pressedLevel(pressedLevel)
{
}

void Button::begin(uint8_t pullMode)
{
    pinMode(pin, pullMode);
    wasPressed = digitalRead(pin) == pressedLevel;
    lastChange = 0;
}

void Button::setDebounce(uint32_t debounceMs)
{
    debounceMs = debounceMs;
}

bool Button::justPressed()
{
    const bool pressed = digitalRead(pin) == pressedLevel;
    const uint32_t now = millis();
    if (pressed == wasPressed || now - lastChange < debounceMs)
    {
        return false;
    }

    wasPressed = pressed;
    lastChange = now;
    return pressed;
}

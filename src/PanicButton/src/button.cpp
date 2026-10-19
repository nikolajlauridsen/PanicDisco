#include "button.h"

Button::Button(gpio_num_t pin, int pressedLevel) : pin_(pin), pressedLevel_(pressedLevel)
{
}

void Button::begin(uint8_t pullMode)
{
    pinMode(pin_, pullMode);
    wasPressed_ = digitalRead(pin_) == pressedLevel_;
    lastChange_ = 0;
}

void Button::setDebounce(uint32_t debounceMs)
{
    debounceMs_ = debounceMs;
}

bool Button::justPressed()
{
    const bool pressed = digitalRead(pin_) == pressedLevel_;
    const uint32_t now = millis();
    if (pressed == wasPressed_ || now - lastChange_ < debounceMs_)
    {
        return false;
    }

    wasPressed_ = pressed;
    lastChange_ = now;
    return pressed;
}

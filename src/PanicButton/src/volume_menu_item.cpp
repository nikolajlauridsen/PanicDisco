#include <Arduino.h>

#include "volume_menu_item.h"
#include "display.h"
#include "controls.h"
#include "pinout.h"
#include "log.h"

const char* VolumeMenuItem::getLabel() const
{
    return "Volume";
}

RTC_DATA_ATTR uint8_t volume = 24;
uint8_t oldVolume = volume;
void VolumeMenuItem::onSelect()
{
    display::writeCentered("Volume", -4);
    display::drawProgressBar(volume, 5);
    display::update();

    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue)
        {
        case controls::RIGHT:
            if (volume < 100)
            {
                volume += 2;
            }
            LOG("Moving right...\n");
            break;
        case controls::LEFT:
            if (volume > 0)
            {
                volume -= 2;
            }
            LOG("Moving left...\n");
            break;
        case controls::ENTER:
            LOG("Enter pushed...\n");
            return;
        case controls::BACK:
            LOG("Back pushed...\n");
            break;
        }

        if (oldVolume != volume)
        {
            display::drawProgressBar(volume, 5);
            display::update();
            oldVolume = volume;
            LOG("Updating display %d volume\n", volume);
        }
    }
}
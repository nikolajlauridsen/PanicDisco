#include <Arduino.h>

#include "label_menu_item.h"
#include "pinout.h"
#include "controls.h"
#include "display.h"

LabelMenuItem::LabelMenuItem(char* label) : label(label)
{
}

const char* LabelMenuItem::getLabel() const
{
    return label;
}

void LabelMenuItem::onSelect()
{
    display::writeCentered(label);
    display::update();

    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue) {
            case controls::ENTER:
            case controls::BACK:
            return;
        }
    }
}
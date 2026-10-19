#pragma once

#include <Arduino.h>

namespace display
{
    void begin();

    void clear();

    void update();

    void setFont(int font);

    void writeCenteredX(const char* text, int row);

    void writeCentered(const char* text, int16_t yOffSet = 0);

    void drawProgressBar(uint8_t progress, int16_t yOffSet = 0, uint16_t width = 110, uint16_t height = 12);
}
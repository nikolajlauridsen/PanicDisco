#include <Arduino.h>
#include <OneBitDisplay.h>

namespace display
{
    // 128×64 display
    ONE_BIT_DISPLAY screen;

    void clear()
    {
        screen.fillScreen(OBD_WHITE);
        screen.display();
    }

    void update()
    {
        screen.display();
    }

    void begin()
    {
        screen.setI2CPins(SDA, SCL);
        screen.I2Cbegin();
        screen.allocBuffer();
        screen.setRotation(0);
        screen.setFont(FONT_SMALL);
        clear();
    }

    void setFont(int font)
    {
        screen.setFont(font);
    }

    void writeCenteredX(const char* text, int row)
    {
        BB_RECT box;
        screen.getStringBox(text, &box);
        screen.drawString(text, (screen.width() - box.w) / 2, (box.h * row));
    }

    void writeCentered(const char* text, int16_t yOffSet)
    {
        BB_RECT box;
        screen.getStringBox(text, &box);
        screen.drawString(text, (screen.width() - box.w) / 2, (screen.height() - box.h) / 2 + yOffSet);
    }

    void drawProgressBar(uint8_t progress, int16_t yOffSet, uint16_t width, uint16_t height)
    {
        const uint16_t x = (screen.width() - width) / 2;
        const uint16_t y = ((screen.height() - height) / 2) + yOffSet;
        screen.drawRect(x, y, width, height, OBD_BLACK);

        constexpr uint16_t inset = 2;
        const uint16_t innerWidth = width - 2 * inset;
        const uint16_t fillWidth = (innerWidth * min<uint8_t>(progress, 100)) / 100;

        // "Clear" the inner rectancle, this is nececary if the progress bar reduces, otherwise the old larger on would stick around
        screen.fillRect(x + inset, y + inset, innerWidth, height - 2 * inset, OBD_WHITE);
        if (fillWidth > 0)
        {
            screen.fillRect(x + inset, y + inset, fillWidth, height - 2 * inset, OBD_BLACK);
        }
    }
} // namespace display
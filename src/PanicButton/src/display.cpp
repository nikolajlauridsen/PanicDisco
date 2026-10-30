#include "log.h"
#include "menu/menu.h"
#include "menu/menu_item.h"
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

        // "Clear" the inner rectancle, this is nececary if the progress bar reduces, otherwise the old larger on would
        // stick around
        screen.fillRect(x + inset, y + inset, innerWidth, height - 2 * inset, OBD_WHITE);
        if (fillWidth > 0)
        {
            screen.fillRect(x + inset, y + inset, fillWidth, height - 2 * inset, OBD_BLACK);
        }
    }

    void renderMenu(Menu* menu)
    {
        clear();

        // Measure one label to find the row height; every built-in font has a fixed height.
        BB_RECT box;
        screen.getStringBox(menu->getSelected().getLabel(), &box);
        if (box.h == 0)
        {
            // Shouldn't happen but better be sure.
            LOG("Selected rendered as 0 height, probably empty string, can't render.");
            return;
        }

        const int totalRows = screen.height() + 5 / box.h;
        // The selected item sits on this row, with the rest spread above and below it.
        const int centerRow = (totalRows - 1) / 2;
        const int cursor = menu->getCursor();
        const int size = menu->size();

        for (int row = 0; row < totalRows; row++)
        {
            // Row 0 is centerRow items before the cursor, the last row is the same distance after it.
            const int index = cursor + (row - centerRow);
            if (index < 0 || index >= size)
            {
                continue;
            }

            if (index == cursor)
            {
                // Invert the whole row so the selection stands out: black band, white text.
                screen.setTextColor(OBD_WHITE, OBD_BLACK);
                writeCenteredX(menu->get(index).getLabel(), row);
                screen.setTextColor(OBD_BLACK, OBD_WHITE);
            }
            else
            {
                writeCenteredX(menu->get(index).getLabel(), row);
            }
        }

        update();
    }

} // namespace display
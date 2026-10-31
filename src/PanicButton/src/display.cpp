#include "log.h"
#include "menu/menu.h"
#include "menu/menu_item.h"
#include <Arduino.h>
#include <OneBitDisplay.h>

namespace display
{
    // 128×64 display
    ONE_BIT_DISPLAY screen;
    static int currentFont = FONT_NORMAL;

    /**
     * Height in pixels of one text row in the current built-in font.
     *
     * Not taken from getStringBox(): the library reports the built-in fonts one pixel taller than they
     * are (6x8 comes back as 9), which spaces rows 9 px apart and loses the eighth row on a 64 px display.
     * Built-in fonts are also drawn in whole 8 px pages, so rows must start at a multiple of 8 anyway.
     */
    static int rowHeight()
    {
        switch (currentFont)
        {
        case FONT_12x16:
        case FONT_16x16:
            return 16;
        case FONT_16x32:
            return 32;
        default: // FONT_6x8, FONT_8x8
            return 8;
        }
    }

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
        currentFont = FONT_SMALL;
        screen.setFont(currentFont);
        clear();
    }

    void setFont(int font)
    {
        currentFont = font;
        screen.setFont(font);
    }

    void writeCenteredX(const char* text, int row)
    {
        BB_RECT box;
        screen.getStringBox(text, &box);
        screen.drawString(text, (screen.width() - box.w) / 2, row * rowHeight());
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
        const int previousFont = currentFont;

        // 8 rows of 8 px on the 64 px display with the small font; fills the screen exactly.
        const int totalRows = screen.height() / rowHeight();
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
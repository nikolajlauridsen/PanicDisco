#pragma once

#include <Arduino.h>
#include "menu/menu.h"
#include <OneBitDisplay.h>

/**
 * The 128x64 I2C OLED and every drawing primitive used on it.
 *
 * Owns the single ONE_BIT_DISPLAY instance; nothing else touches the screen
 * object. Drawing goes into an in-memory buffer and only reaches the panel on
 * update(), so group several draw calls and call update() once. Coordinates
 * are in pixels with (0, 0) top-left; a positive yOffSet moves things down.
 */
namespace display
{
    /**
     * Initialises I2C, allocates the frame buffer, selects FONT_12x16 and
     * clears the screen. Call once before any other display function.
     */
    void begin();

    /**
     * Blanks the whole screen and pushes it to the panel immediately.
     */
    void clear();

    /**
     * Pushes the frame buffer to the panel. Nothing drawn is visible until
     * this is called.
     */
    void update();

    /**
     * Selects one of OneBitDisplay's built-in fonts (FONT_6x8, FONT_8x8,
     * FONT_12x16, FONT_16x16, FONT_16x32) for subsequent text calls. Also
     * sets the row height used by writeCenteredX() and renderMenu().
     */
    void setFont(int font);

    /**
     * Draws text horizontally centred on a given text row.
     *
     * @param text NUL-terminated string to draw.
     * @param row  0-based row, each one font-height tall from the top of the
     *             screen. With the small font that gives 8 rows on 64 px.
     */
    void writeCenteredX(const char* text, int row);

    /**
     * Draws text centred both horizontally and vertically.
     *
     * @param text    NUL-terminated string to draw.
     * @param yOffSet pixels to shift from the vertical centre, positive = down.
     */
    void writeCentered(const char* text, int16_t yOffSet = 0);

    /**
     * Draws a horizontally centred progress bar: an outline with a filled
     * portion proportional to progress. Clears the inside first so it can be
     * redrawn in place when the value goes down.
     *
     * @param progress 0-100, values above 100 are treated as 100.
     * @param yOffSet  pixels to shift from the vertical centre, positive = down.
     * @param width    outer width in pixels.
     * @param height   outer height in pixels.
     */
    void drawProgressBar(uint8_t progress, int16_t yOffSet = 0, uint16_t width = 110, uint16_t height = 12);

    /**
     * Clears the screen and draws the menu, then calls update().
     *
     * The selected item sits on the middle row, drawn inverted (white text on
     * a black band), with the items before and after it filling the rows
     * above and below. Rows that would fall outside the menu are left blank.
     * Uses the current font; the row count is the screen height divided by
     * the font height.
     *
     * @param menu the menu to draw. Only read, not modified.
     */
    void renderMenu(Menu* menu);
}

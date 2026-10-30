#pragma once

/**
 * Base class for anything that can appear as a row in a Menu.
 *
 * The only thing the menu framework needs from an item is a label to draw.
 * Derive from this (or ActionMenuItem, if selecting the row should do
 * something) and return the row text from getLabel().
 */
struct MenuItem
{
    virtual ~MenuItem() = default;

    /**
     * @return the text drawn for this row. The pointer must stay valid for as
     *         long as the item is in a menu; it is not copied.
     */
    virtual const char* getLabel() const = 0;
};

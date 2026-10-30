#pragma once

#include "menu_item.h"
#include <cstddef>

/**
 * A vertical list of MenuItems with a cursor.
 *
 * This base class owns only the cursor (which row is highlighted) and how it
 * moves. Where the items come from and how they are stored is up to the
 * derived class, which supplies them through getSelected()/get()/size().
 * Rendering is done elsewhere (display::renderMenu) by iterating get(index)
 * for index in [0, size()) and highlighting the row at getCursor().
 */
class Menu
{
  public:
    virtual ~Menu() = default;

    /**
     * @return the item the cursor currently points at.
     */
    virtual MenuItem& getSelected() = 0;

    /**
     * @param index row number, 0-based. Must be < size().
     * @return the item at that row.
     */
    virtual MenuItem& get(size_t index) = 0;

    /**
     * @return the number of items in the menu.
     */
    virtual size_t size() const = 0;

    /**
     * Moves the cursor one row down. Stops at the last row, no wrap-around.
     * @return true if the cursor moved, false if it was already on the last row.
     */
    bool moveNext()
    {
        if (cursor + 1 < size())
        {
            cursor++;
            return true;
        }

        return false;
    }

    /**
     * Moves the cursor one row up. Stops at the first row, no wrap-around.
     * @return true if the cursor moved, false if it was already on the first row.
     */
    bool movePrevious()
    {
        if (cursor > 0)
        {
            cursor--;
            return true;
        }

        return false;
    }

    /**
     * @return the 0-based row the cursor is on.
     */
    size_t getCursor() const
    {
        return cursor;
    }

  private:
    size_t cursor = 0;
};

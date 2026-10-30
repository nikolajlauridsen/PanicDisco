#pragma once

#include "menu_item.h"
#include <cstddef>

class Menu
{
  public:
    virtual ~Menu() = default;

    /**
     * @return the item the cursor currently points at.
     */
    virtual MenuItem& getSelected() = 0;

    /**
     * @return the number of items in the menu.
     */
    virtual size_t size() const = 0;

    bool moveNext()
    {
        if (cursor + 1 < size())
        {
            cursor++;
            return true;
        }

        return false;
    }

    bool movePrevious()
    {
        if (cursor > 0)
        {
            cursor--;
            return true;
        }

        return false;
    }

    size_t getCursor() const
    {
        return cursor;
    }

  private:
    size_t cursor = 0;
};

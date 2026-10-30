#pragma once

#include "menu_item.h"

/**
 * A MenuItem that does something when the user presses ENTER on it.
 *
 * While onSelect() runs the item owns the screen and the controls: it should
 * draw its own UI, poll controls::read() and return when the user is done
 * (ENTER/BACK) or the lid closes. The caller re-renders the menu afterwards.
 */
struct ActionMenuItem : public MenuItem
{
    /**
     * Runs when this item is selected. Blocks until the item is finished.
     */
    virtual void onSelect() = 0;
};

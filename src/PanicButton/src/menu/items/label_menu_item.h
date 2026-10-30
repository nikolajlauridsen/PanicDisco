#pragma once

#include "menu/action_menu_item.h"

/**
 * Placeholder menu entry: shows its own label full-screen when selected and
 * returns on ENTER or BACK. Useful for filling out a menu before the real
 * item exists.
 */
class LabelMenuItem : public ActionMenuItem
{

  public:
    /**
     * @param label the row text, also what's shown when selected. Not copied -
     *              pass a string literal or something that outlives the item.
     */
    explicit LabelMenuItem(char* Label);

    const char* getLabel() const override;
    void onSelect() override;

  private:
    char* label = 0;
};

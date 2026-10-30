#pragma once

#include "action_menu_item.h"
#include "menu.h"
#include <span>

/**
 * A Menu over a fixed list of ActionMenuItems, where ENTER runs the selected
 * item's onSelect().
 *
 * The menu does not own its items: it keeps a std::span over an array of
 * pointers the caller provides, so both the items and the array must outlive
 * the menu. In practice that means declaring them `static` (see
 * handleLidOpened() in main.cpp); a temporary array would dangle.
 *
 * getSelected()/get() return ActionMenuItem& (a covariant override of the
 * MenuItem& in Menu) so callers get the typed item without a cast.
 */
class ActionMenu : public Menu
{
  public:
    /**
     * @param items the rows, in display order. Not copied - must stay alive
     *              for as long as the menu is used.
     */
    explicit ActionMenu(std::span<ActionMenuItem* const> items);

    ActionMenuItem& getSelected() override;

    ActionMenuItem& get(size_t index) override;

    size_t size() const override;

    /**
     * Runs onSelect() on the item the cursor currently points at. Blocks until
     * that item returns.
     */
    void select();

  private:
    std::span<ActionMenuItem* const> menuItems;
};

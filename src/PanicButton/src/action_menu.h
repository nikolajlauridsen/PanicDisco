#pragma once

#include "action_menu_item.h"
#include "menu.h"
#include <span>

class ActionMenu : public Menu
{
  public:
    explicit ActionMenu(std::span<ActionMenuItem* const> items);

    ActionMenuItem& getSelected() override;

    ActionMenuItem& get(size_t index) override;

    size_t size() const override;

    /**
     * Runs onSelect() on the item the cursor currently points at.
     */
    void select();

  private:
    std::span<ActionMenuItem* const> menuItems;
};

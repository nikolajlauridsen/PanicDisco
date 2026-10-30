#include "action_menu.h"

ActionMenu::ActionMenu(std::span<ActionMenuItem* const> items) : menuItems(items)
{
}

ActionMenuItem& ActionMenu::getSelected()
{
    return *menuItems[getCursor()];
}

size_t ActionMenu::size() const
{
    return menuItems.size();
}

void ActionMenu::select()
{
    getSelected().onSelect();
}

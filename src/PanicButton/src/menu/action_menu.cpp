#include "action_menu.h"

ActionMenu::ActionMenu(std::span<ActionMenuItem* const> items) : menuItems(items)
{
}

ActionMenuItem& ActionMenu::getSelected()
{
    return get(getCursor());
}

ActionMenuItem& ActionMenu::get(size_t index)
{
    return *menuItems[index];
}

size_t ActionMenu::size() const
{
    return menuItems.size();
}

void ActionMenu::select()
{
    getSelected().onSelect();
}

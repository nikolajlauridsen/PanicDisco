#pragma once

#include "menu_item.h"

struct ActionMenuItem : public MenuItem
{
    virtual void onSelect() = 0;
};
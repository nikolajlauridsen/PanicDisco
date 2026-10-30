#pragma once

#include "menu/action_menu_item.h"

class VolumeMenuItem : public ActionMenuItem
{
  public:
    const char* getLabel() const override;
    void onSelect() override;
};
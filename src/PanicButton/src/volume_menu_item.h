#pragma once

#include "action_menu_item.h"

class VolumeMenuItem : public ActionMenuItem
{
  public:
    const char* getLabel() const override;
    void onSelect() override;
};
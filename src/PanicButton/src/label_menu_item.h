#pragma once

#include "action_menu_item.h"

class LabelMenuItem : public ActionMenuItem
{

  public:
    explicit LabelMenuItem(char* Label);

    const char* getLabel() const override;
    void onSelect() override;

  private:
    char* label = 0;
};
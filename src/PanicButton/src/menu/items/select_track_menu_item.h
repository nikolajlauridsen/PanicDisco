#pragma once

#include "disco_client.h"
#include "menu/action_menu_item.h"

class SelectTrackMenuItem : public ActionMenuItem
{
  public:
    explicit SelectTrackMenuItem(DiscoClient& client);
    const char* getLabel() const override;
    void onSelect() override;

  private:
    DiscoClient& client;
};
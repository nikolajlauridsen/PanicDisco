#pragma once

#include "menu/action_menu_item.h"

/**
 * Menu entry for adjusting the playback volume.
 *
 * When selected it draws a progress bar and adjusts the volume in steps of 2
 * (0-100) on LEFT/RIGHT until ENTER or BACK is pressed or the lid closes. The
 * value is kept in RTC_DATA_ATTR memory so it survives deep sleep. It is not
 * yet sent to the server.
 */
class VolumeMenuItem : public ActionMenuItem
{
  public:
    const char* getLabel() const override;
    void onSelect() override;
};

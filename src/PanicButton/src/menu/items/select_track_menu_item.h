#pragma once

#include "disco_client.h"
#include "menu/action_menu_item.h"
#include "track_entity.h"

/**
 * Menu entry that fetches the track list from the server and lets the user
 * pick which one the boombox should play.
 *
 * On select it connects to Wi-Fi if needed, calls DiscoClient::getTracks(),
 * shows the result as a TrackMenu and, on ENTER, loads the highlighted track
 * via DiscoClient::loadTrack(). Returns after a successful load, on BACK, or
 * when the lid closes. Network or server failures are shown on screen and
 * dismissed with ENTER/BACK.
 */
class SelectTrackMenuItem : public ActionMenuItem
{
  public:
    /**
     * @param client the server client to use. Not copied - must outlive the
     *               item (in practice the static one in main.cpp).
     */
    explicit SelectTrackMenuItem(DiscoClient& client);
    const char* getLabel() const override;
    void onSelect() override;

  private:
    DiscoClient& client;

    /**
     * Blocks until the user presses ENTER or BACK, or the lid closes. Used to
     * hold an error message on screen until acknowledged.
     */
    void waitForReturn();

    /**
     * Asks the server to load one track and shows the outcome briefly.
     * @return true if the server answered 200.
     */
    bool loadTrack(TrackEntity& track);
};

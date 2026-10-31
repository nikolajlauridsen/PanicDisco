#include <Arduino.h>

#include "../track_menu.h"
#include "HTTPClient.h"
#include "controls.h"
#include "display.h"
#include "log.h"
#include "pinout.h"
#include "select_track_menu_item.h"
#include "wifi_connection.h"

SelectTrackMenuItem::SelectTrackMenuItem(DiscoClient& client) : client(client)
{
}

const char* SelectTrackMenuItem::getLabel() const
{
    return "Select Track";
}

void SelectTrackMenuItem::waitForReturn()
{
    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue)
        {
        case controls::ENTER:
        case controls::BACK:
            return;
        }
    }
}

bool SelectTrackMenuItem::loadTrack(TrackEntity& track)
{
    int status = client.loadTrack(track);
    if (status == HTTP_CODE_OK)
    {
        display::clear();
        display::writeCentered("Track loaded");
        display::update();
        delay(500);
        display::clear();
        return true;
    }

    display::clear();
    display::writeCentered("Track failed to load");
    LOG("Track failed to load, status: %d\n", status);
    delay(500);
    display::clear();
    return false;
}

void SelectTrackMenuItem::onSelect()
{
    // Connect to wifi only if not already connected.
    if (!wifi_connection::isConnected())
    {
        if (!wifi_connection::connect())
        {
            display::clear();
            display::writeCentered("No Wi-Fi");
            display::update();
            waitForReturn();
            return;
        }
    }

    display::setFont(FONT_SMALL);
    display::writeCentered("Fetching tracks...");
    display::update();

    std::vector<TrackEntity> tracks;
    int statusCode = client.getTracks(tracks);

    if (statusCode != HTTP_CODE_OK)
    {
        LOG("getTracks failed: %d\n", statusCode);
        display::writeCentered("No Tracks");
        display::writeCentered((String("Status: ") + statusCode).c_str(), 10);
        display::update();
        waitForReturn();
        return;
    }

    TrackMenu menu(tracks);
    display::renderMenu(&menu);

    while (digitalRead(REED_PIN) == HIGH)
    {
        int controlsValue = controls::read();

        switch (controlsValue)
        {
        case controls::RIGHT:
            menu.moveNext();
            display::renderMenu(&menu);
            break;
        case controls::LEFT:
            menu.movePrevious();
            display::renderMenu(&menu);
            break;
        case controls::ENTER:
        {
            bool succeess = loadTrack(menu.getSelected());
            if (succeess)
            {
                return;
            }
            display::renderMenu(&menu);
            break;
        }
        case controls::BACK:
            return;
        }
    }
}

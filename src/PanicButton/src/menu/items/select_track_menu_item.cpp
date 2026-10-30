#include <Arduino.h>

#include "../track_menu.h"
#include "HTTPClient.h"
#include "controls.h"
#include "display.h"
#include "log.h"
#include "pinout.h"
#include "select_track_menu_item.h"

SelectTrackMenuItem::SelectTrackMenuItem(DiscoClient& client) : client(client)
{
}

const char* SelectTrackMenuItem::getLabel() const
{
    return "Select Track";
}

void waitForReturn()
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

void SelectTrackMenuItem::onSelect()
{
    display::setFont(FONT_SMALL);
    display::writeCentered("Fetching tracks...");
    display::update();

    std::vector<TrackEntity> tracks;
    int statusCode = client.getTracks(tracks);

    if (statusCode != HTTP_CODE_OK)
    {
        LOG("getTracks failed: %d\n", statusCode);
        display::writeCentered("No Tracks");
        display::writeCentered(&"Status: "[statusCode], 10);
        display::update();
        waitForReturn();
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
        // TODO: Send load request
        case controls::BACK:
            return;
        }
    }
}

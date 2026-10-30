#pragma once

#include <ArduinoJson.h>

#include <cstddef>
#include <cstring>

#include "menu/menu_item.h"

// One entry of GET /api/tracks - mirrors disco_shared's TrackEntity (id + name).
// It's a MenuItem so a track list can be rendered directly, name as the label.
// Names longer than the buffer are truncated; the OLED shows ~21 chars per row.
struct TrackEntity : public MenuItem
{
    static constexpr size_t MAX_NAME_LENGTH = 31; // +1 for the terminating NUL

    int id = 0;
    char name[MAX_NAME_LENGTH + 1] = "";

    const char* getLabel() const override
    {
        return name;
    }
};

// ArduinoJson converter: enables `variant.as<TrackEntity>()`. Must live in the
// same namespace as TrackEntity so argument-dependent lookup finds it.
inline void convertFromJson(JsonVariantConst source, TrackEntity& destination)
{
    destination.id = source["id"] | 0;

    // source["name"] is a const char* into the JsonDocument's memory, which is
    // freed when the document goes out of scope. Keeping that pointer would
    // leave it dangling, so copy the bytes into our own buffer instead.
    // strlcpy truncates to the buffer size and always NUL-terminates.
    strlcpy(destination.name, source["name"] | "", sizeof(destination.name));
}

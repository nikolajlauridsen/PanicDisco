#pragma once

namespace controls
{
    enum Control
    {
        LEFT = -1,
        RIGHT = 1,
        ENTER = 2,
        BACK = 3,
        NOOP = 0,
    };

    Control read();

    void begin();
}

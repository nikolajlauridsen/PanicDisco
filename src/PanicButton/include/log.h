#pragma once

// Serial logging that only exists in the debug build.
//
// The release build (env:seeed_xiao_esp32c6) never talks on serial, so there
// the macros expand to nothing: no Serial.begin(), no string formatting, no
// flash spent on the messages, and no startup delay. The debug build
// (env:seeed_xiao_esp32c6_debug) defines DEBUG_SERIAL via build_flags.
//
// Usage: LOG("value = %d\n", x);  LOG_BEGIN() once in setup(); LOG_FLUSH()
// before deep sleep so the last lines leave the USB buffer.

#ifdef DEBUG_SERIAL

#include <Arduino.h>

// The XIAO's serial port is the chip's native USB. After a deep-sleep wake,
// Windows takes up to a couple of seconds to re-enumerate it; anything printed
// before that is lost, hence the wait. Debug build only - this is dead time
// on the press-to-request path.
#define LOG_BEGIN()                                                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
        Serial.begin(115200);                                                                                          \
        delay(3000);                                                                                                   \
    } while (0)
#define LOG(...) Serial.printf(__VA_ARGS__)
#define LOG_FLUSH() Serial.flush()

#else

#define LOG_BEGIN()                                                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
    } while (0)
#define LOG(...)                                                                                                       \
    do                                                                                                                 \
    {                                                                                                                  \
    } while (0)
#define LOG_FLUSH()                                                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
    } while (0)

#endif

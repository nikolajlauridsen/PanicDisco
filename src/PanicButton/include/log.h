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
//
// The TX timeout is zeroed because the core's USB CDC write otherwise blocks
// (up to ~2 s per call) once the host's read buffer fills, which happens
// whenever the cable is plugged in but no serial monitor is open. That stalls
// any loop that logs, e.g. the encoder polling. Lost lines beat a frozen device.
#define LOG_BEGIN()                                                                                                    \
    do                                                                                                                 \
    {                                                                                                                  \
        Serial.begin(115200);                                                                                          \
        Serial.setTxTimeoutMs(0); /* drop output instead of blocking when nothing reads the port */                    \
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

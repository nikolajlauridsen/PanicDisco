#include <Arduino.h>

// The XIAO ESP32C6's user LED (GPIO 15) is active low:
// LOW turns it on, HIGH turns it off.

// uint32_t: the "_t" suffix means "type" - a typedef from <stdint.h>, not a
// built-in keyword. Fixed-width types guarantee exactly 32 bits on any platform,
// unlike plain int/long whose size varies.
static constexpr uint32_t BLINK_INTERVAL_MS = 500;

void setup()
{
    Serial.begin(115200);
}

void loop()
{
    Serial.println("Hello world");
    delay(1000);
}

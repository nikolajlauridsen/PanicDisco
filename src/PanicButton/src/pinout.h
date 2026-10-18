#include <Arduino.h>

/*
NOTE:
======
Bit mask of GPIO numbers which will cause wakeup. Only GPIOs
which have RTC functionality can be used in this bit map.
For different SoCs, the related GPIOs are:
- ESP32: 0, 2, 4, 12-15, 25-27, 32-39
- ESP32-S2: 0-21
- ESP32-S3: 0-21
- ESP32-C6: 0-7
- ESP32-H2: 7-14
*/
static constexpr gpio_num_t PANIC_BUTTON_PIN = GPIO_NUM_0;
static constexpr gpio_num_t REED_PIN = GPIO_NUM_1;
static constexpr gpio_num_t PIN_A = GPIO_NUM_19;
static constexpr gpio_num_t PIN_B = GPIO_NUM_17;
#define BUTTON_PIN_BITMASK (1ULL << PANIC_BUTTON_PIN)
#define REED_PIN_BITMASK (1ULL << REED_PIN)
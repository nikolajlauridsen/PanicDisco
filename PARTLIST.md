# PanicDisco Hardware Part List

## Server (ceiling-mounted Raspberry Pi)

Parts for the ceiling-mounted Raspberry Pi build (audio + lights triggered via the panic endpoint).

| Component | Model / Part | Qty | Specs | Notes / Status | Link | 
|---|---|---|---|---|---|
| Audio amp | Adafruit MAX98357A I2S Class-D Mono Amp | 2 | 3W @ 4Ω, 5V, I2S digital input | Need 2 for stereo (one as I2S clock master, one follower per Adafruit's guide) | https://www.amazon.de/stk-MAX98357A-forst%C3%A6rkermodul-ESP32-Raspberry/dp/B0F8ZJZ4BZ | 
| Relay board | ELEGOO 4-Channel 5V Relay Module w/ Optocoupler | 1 | 5V coil, opto-isolated, low-level trigger, IN1-4 take 3.3V from Pi GPIO fine | Remove the JD-VCC jumper and power relay coils (JD-VCC/VCC) from a separate 5V supply (same PSU as the amp), not the Pi's 5V rail — 4 relays energized at once can pull ~300mA | https://www.amazon.de/ELEGOO-4-Channel-Relay-Module-Optocoupler/dp/B01M8G4Y7Z/ |
| PSU | Mean Well IRM-60-5ST | 1 | AC-DC converter, 85-305VAC in, 5V/12A (60W) out, open-frame/potted module | Powers Pi 4 (3A) + 2x amps (~1.2A) + relay coils (~0.3A) with headroom for thermal derating in an enclosed ceiling space and future relay/light expansion. Open-frame — needs mounting in a proper enclosure with strain relief on the mains leads. Sized for a lamp-outlet feed instead of a plug-in brick PSU | https://www.amazon.de/-/en/MNMIOIO-1005005971563652/dp/B0GV25KGN3 |

## Panic button (battery-powered controller)

Parts for the handheld panic button that talks to `disco_server`'s `/api/panic` and `/api/boombox` endpoints over WiFi. Designed around deep sleep: the ESP32-C6 sleeps at ~15 µA and is woken by a GPIO edge from the panic/wake button; the OLED is fully powered off via the MOSFET while asleep, not just blanked. Schematic in `Schematics/PanicButton/`.

| Component | Model / Part | Qty | Specs | Notes / Status | Link |
|---|---|---|---|---|---|
| Microcontroller | Seeed Studio XIAO ESP32-C6 | 1 | ESP32-C6 (RISC-V 160 MHz), WiFi 6 2.4 GHz, BLE 5.3, 512 KB SRAM, 16 KB LP SRAM, 4 MB flash, USB-C, built-in LiPo charger with BAT+/BAT- pads on the underside, ~15 µA deep sleep (chip-level figure per Seeed) | Chosen over Pi Zero W (no sleep mode, ~100 mA idle) and generic ESP32 DevKits (USB-serial chip + LDO leak mA in sleep). Only GPIO0–7 are low-power pins that can wake from deep sleep — put the panic/wake buttons there; I2C is on D4 (SDA) / D5 (SCL). Firmware must set the RF switch for the onboard antenna (see Seeed wiki). No battery voltage sense on board — add a resistor divider to an ADC pin if a battery gauge is wanted. Power from a single 3.7 V LiPo/18650 on the BAT pads | https://www.amazon.de/-/en/Seeed-Studio-XIAO-ESP32C6-Compatible/dp/B0D2NKVB34 (alt: https://www.berrybase.de/en/seeed-xiao-esp32-c6-wi-fi-6-ble-5.0-zigbee-thread-512kb-sram-4mb-flash-uart-spi-risc-v) |
| OLED display | 0.96" SSD1306 128x64 I2C module (generic 4-pin: GND/VCC/SCL/SDA) | 1 | 3.3–5 V, I2C addr 0x3C, ~20 mA max with full screen lit, 1 KB framebuffer | Any generic SSD1306 (or SH1106 1.3") module works; driven with u8g2 or Adafruit SSD1306 from the XIAO's D4/D5 I2C pins. VCC goes through the MOSFET below, not straight to 3.3 V, so it draws nothing in deep sleep; re-init the display on every wake. Linked listing is a reference for the module type — buy any equivalent from an EU seller | https://www.amazon.com/DIYmall-Serial-128x64-Display-Arduino/dp/B00O2KDQBE |
| OLED power switch | AO3401A P-channel MOSFET, SOT-23 | 1 | -30 V, -4 A, Vgs(th) ≈ -1 V, logic-level so it switches fully at 3.3 V gate drive | High-side switch on the OLED's VCC: source to 3.3 V, drain to OLED VCC, gate to a XIAO GPIO. Add a 100 kΩ pull-up from gate to 3.3 V so the MOSFET stays off while the GPIO is high-impedance in deep sleep; drive the GPIO low to power the display. Massively overrated for a 20 mA load — chosen because it's cheap, common, and logic-level. Any logic-level P-channel (e.g. DMG2305UX, IRLML6402) is a drop-in | https://www.amazon.com/AO3401A-AO3401-SOT-23-P-Channel-Transistor/dp/B0G75TVBKS |

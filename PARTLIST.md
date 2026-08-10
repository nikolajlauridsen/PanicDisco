# PanicDisco Server Hardware Part List

Parts for the ceiling-mounted Raspberry Pi build (audio + lights triggered via the panic endpoint).

| Component | Model / Part | Qty | Specs | Notes / Status | Link | 
|---|---|---|---|---|---|
| Audio amp | Adafruit MAX98357A I2S Class-D Mono Amp | 2 | 3W @ 4Ω, 5V, I2S digital input | Need 2 for stereo (one as I2S clock master, one follower per Adafruit's guide) | https://www.amazon.de/stk-MAX98357A-forst%C3%A6rkermodul-ESP32-Raspberry/dp/B0F8ZJZ4BZ | 
| Relay board | ELEGOO 4-Channel 5V Relay Module w/ Optocoupler | 1 | 5V coil, opto-isolated, low-level trigger, IN1-4 take 3.3V from Pi GPIO fine | Remove the JD-VCC jumper and power relay coils (JD-VCC/VCC) from a separate 5V supply (same PSU as the amp), not the Pi's 5V rail — 4 relays energized at once can pull ~300mA | https://www.amazon.de/ELEGOO-4-Channel-Relay-Module-Optocoupler/dp/B01M8G4Y7Z/ |
| PSU | Mean Well IRM-60-5ST | 1 | AC-DC converter, 85-305VAC in, 5V/12A (60W) out, open-frame/potted module | Powers Pi 4 (3A) + 2x amps (~1.2A) + relay coils (~0.3A) with headroom for thermal derating in an enclosed ceiling space and future relay/light expansion. Open-frame — needs mounting in a proper enclosure with strain relief on the mains leads. Sized for a lamp-outlet feed instead of a plug-in brick PSU | https://www.amazon.de/-/en/MNMIOIO-1005005971563652/dp/B0GV25KGN3 |


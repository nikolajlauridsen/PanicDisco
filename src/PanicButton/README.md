# PanicButton

Firmware for the panic button itself: a [Seeed Studio XIAO ESP32-C6](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/)
built with [PlatformIO](https://platformio.org/) and the Arduino framework. It will eventually talk to `disco_server`'s
panic API (`POST /api/panic/start` / `POST /api/panic/stop`) over Wi-Fi; right now it's a bring-up sketch.

## Prerequisites

* VS Code with the [PlatformIO IDE](https://marketplace.visualstudio.com/items?itemName=platformio.platformio-ide) extension
  (or the standalone `pio` CLI, found at `~/.platformio/penv/Scripts/pio.exe` on Windows if it isn't on your PATH).
* The [clangd](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.vscode-clangd) extension for
  IntelliSense — see below. VS Code will offer to install it from the workspace recommendations.

The ESP32 toolchain, Arduino core and everything else is downloaded automatically by PlatformIO on the first build.

> **Windows, first build only:** run it from PowerShell, cmd, or the PlatformIO IDE — **not Git Bash**. The one-time
> toolchain install runs ESP-IDF's `idf_tools.py`, which aborts with `MSys/Mingw is not supported` if the `MSYSTEM`
> environment variable is set. Once the toolchain is installed, building from Git Bash works fine.

## Build, flash, monitor

Run from this directory (`src/PanicButton`):

```bash
pio run                  # build
pio run -t upload        # build + flash (board plugged in; port is auto-detected)
pio device monitor       # serial monitor at 115200 baud (monitor_speed in platformio.ini)
```

Or use the PlatformIO toolbar buttons at the bottom of VS Code, which do the same thing.

## IntelliSense (clangd)

Code completion, navigation and diagnostics come from **clangd**, not the Microsoft C/C++ extension — the latter is
deliberately disabled in `.vscode/settings.json` so the two don't fight. clangd reads `compile_commands.json` in this
directory, which PlatformIO generates from the real build:

```bash
pio run -t compiledb
```

**Rerun that command whenever you:**

* add or rename a source file under `src/`, `include/` or `lib/`
* add a library dependency (`lib_deps` in `platformio.ini`, or a folder under `lib/`)
* change `build_flags` or anything else in `platformio.ini`

Until you do, clangd guesses the flags for new files from neighbouring ones. That usually works, but it's also the
cause of any phantom "file not found" or "unknown type" errors that the real build doesn't have — if IntelliSense and
`pio run` disagree, regenerate the database first.

`compile_commands.json` is gitignored (it contains absolute machine-specific paths). `.clangd` tells clangd where the
RISC-V `g++` from the PlatformIO toolchain lives, since the compile database only names it bare and it's not on your
normal PATH; the path in there assumes the default `~/.platformio` location.

## Why the pioarduino platform?

`platformio.ini` uses the community [pioarduino](https://github.com/pioarduino/platform-espressif32) fork of the
`espressif32` platform rather than the official one. The official platform only ships Arduino-ESP32 core 2.x, which has
no ESP32-C6 support — its board definition for `seeed_xiao_esp32c6` lists ESP-IDF as the only framework. The C6 needs
Arduino-ESP32 3.x, which pioarduino provides. Don't "fix" the platform line back to `espressif32`; `#include <Arduino.h>`
stops resolving.

## Hardware notes

* The onboard user LED is `LED_BUILTIN` (GPIO 15) and is **active low**: `digitalWrite(LED_BUILTIN, LOW)` turns it on.
* Pinout and specs: [Seeed wiki](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/).

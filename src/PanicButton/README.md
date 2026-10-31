# PanicButton

Firmware for the panic button itself: a [Seeed Studio XIAO ESP32-C6](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/)
built with [PlatformIO](https://platformio.org/) and the Arduino framework. It sleeps until either the panic button
is pressed or the lid is opened. Button: connect to Wi-Fi and call `disco_server`'s panic API (`POST /api/panic/start`,
then `POST /api/panic/stop` once the button is twisted back). Lid: show a menu on the OLED, driven by a rotary
encoder, until the lid is closed again. The menu has a volume setting and a track picker that fetches the track list
(`GET /api/tracks`) and cues the chosen one up in the server's boombox (`PUT /api/boombox/load/<id>`).

## Layout

```
src/
  main.cpp              wake -> reed switch decides: panic path or menu path -> deep sleep; nothing else
  wifi_connection.*     fast Wi-Fi reconnect (remembers channel/BSSID across sleep, static IP)
  disco_client.*        DiscoClient: one method per disco_server endpoint (panicStart/panicStop/getTracks/loadTrack)
  track_entity.h        TrackEntity: id + name, the C++ mirror of disco_shared's TrackEntity; also a MenuItem
  pinout.h              every GPIO number in one place (button, reed switch, encoder, enter/back buttons)
  button.*              Button: debounced push button, justPressed() fires once per press
  controls.*            rotary encoder + buttons -> LEFT / RIGHT / ENTER / BACK via controls::read()
  display.*             the OLED: text helpers, progress bar, renderMenu()
  menu/                 menu framework
    menu_item.h           MenuItem: getLabel()
    action_menu_item.h    ActionMenuItem: + onSelect()
    menu.h                Menu: owns the cursor (moveNext/movePrevious), abstract over the items
    action_menu.*         ActionMenu: a Menu of ActionMenuItems, select() runs the chosen one
    track_menu.*          TrackMenu: a Menu over a std::vector<TrackEntity> fetched at runtime
    items/                concrete menu entries (volume_menu_item.*, select_track_menu_item.*, label_menu_item.*)
include/
  log.h                 LOG()/LOG_BEGIN()/LOG_FLUSH(): serial logging in the debug env, nothing in release
  secrets.example.h     template for secrets.h: Wi-Fi credentials, static IP, API base URL
  secrets.h             your copy - gitignored
platformio.ini          board/platform config (portable); huge_app partition table = 3 MB app, no OTA
platformio.local.ini    your COM port etc. - gitignored
```

New server endpoints become methods on `DiscoClient`; `main.cpp` should stay a handful of lines.

JSON goes through [ArduinoJson](https://arduinojson.org/) v7 (`lib_deps`). `DiscoClient::getTracks()` is the pattern
to copy for a new endpoint that returns a body: `http.useHTTP10(true)` (so the body isn't chunked), deserialize
straight from `http.getStream()` through a `DeserializationOption::Filter` that names only the fields you want, then
`item.as<YourStruct>()` via a `convertFromJson(JsonVariantConst, YourStruct&)` free function next to the struct (see
`track_entity.h`). Strings from the document die with it, so copy them into the struct rather than keeping the pointer.

Includes that cross a folder are written from `src/`, which PlatformIO puts on the include path:
`#include "menu/action_menu.h"`, `#include "menu/items/volume_menu_item.h"`. Files in the same folder use the bare
name.

### Adding a menu entry

1. Add `src/menu/items/<name>_menu_item.h` / `.cpp` with a class deriving from `ActionMenuItem`, implementing
   `getLabel()` and `onSelect()`. `onSelect()` owns the screen and the controls until it returns; loop on
   `controls::read()` and return on `ENTER` or `BACK` (see `volume_menu_item.cpp`).
2. In `handleLidOpened()` in `main.cpp`, add a `static` instance and put its address in the `menuItems` array.
   Both must be `static`: `ActionMenu` only holds a view (`std::span`) over that array, it doesn't copy it.
3. Run `pio run -t compiledb` so clangd picks up the new files.

Two things to know when writing `onSelect()`:

* **Talking to the server?** Call `wifi_connection::connect()` first (skip it if `isConnected()`). The lid path
  doesn't connect on wake, and opening a socket before the Wi-Fi stack is up doesn't fail gracefully, it aborts the
  firmware with a `xQueueSemaphoreTake` assert. `select_track_menu_item.cpp` shows the guard.
* **Showing a list that only exists at runtime?** Derive from `Menu` instead of using `ActionMenu`, as `TrackMenu`
  does over a `std::vector<TrackEntity>`. The menu only holds a reference to the data, so declare both in the same
  scope. Text longer than one row is truncated by `display`, so long labels are safe.

## Prerequisites

* VS Code with the [PlatformIO IDE](https://marketplace.visualstudio.com/items?itemName=platformio.platformio-ide) extension
  (or the standalone `pio` CLI, found at `~/.platformio/penv/Scripts/pio.exe` on Windows if it isn't on your PATH).
* The [clangd](https://marketplace.visualstudio.com/items?itemName=llvm-vs-code-extensions.vscode-clangd) extension for
  IntelliSense — see below. VS Code will offer to install it from the workspace recommendations.

The ESP32 toolchain, Arduino core and everything else is downloaded automatically by PlatformIO on the first build.

> **Windows, first build only:** run it from PowerShell, cmd, or the PlatformIO IDE — **not Git Bash**. The one-time
> toolchain install runs ESP-IDF's `idf_tools.py`, which aborts with `MSys/Mingw is not supported` if the `MSYSTEM`
> environment variable is set. Once the toolchain is installed, building from Git Bash works fine.

## Wi-Fi credentials

The sketch reads the network name and password from `include/secrets.h`, which is **gitignored** (this repo is
public). Create it from the committed template and fill it in:

```bash
cp include/secrets.example.h include/secrets.h
```

It holds everything specific to your network, not just the password: the Wi-Fi credentials, the static IP the
button should use (reserve it in your router — static IP is what lets it skip DHCP on every wake), and
`API_BASE_URL` for the `disco_server` instance it should call. If you add more later (tokens, ...), put them in
the same file and mirror the new `#define` with a placeholder in `secrets.example.h` so the template stays complete.

## Build, flash, monitor

Run from this directory (`src/PanicButton`):

```bash
pio run                  # build (the debug env - see below)
pio run -t upload        # build + flash (board plugged in; port is auto-detected)
pio device monitor       # serial monitor at 115200 baud (monitor_speed in platformio.ini)
```

### Debug vs release builds

There are two PlatformIO environments:

| env | what it is |
|---|---|
| `seeed_xiao_esp32c6_debug` | **default** while developing. Serial logging on: `LOG_BEGIN()` opens the port and waits 3 s for Windows to re-enumerate the USB device after a deep-sleep wake, so you actually see the output. |
| `seeed_xiao_esp32c6` | the release build for the real button. Identical, except the `LOG*` macros in `include/log.h` compile to nothing: no serial, no 3 s wait, no log strings in the binary. |

```bash
pio run -e seeed_xiao_esp32c6 -t upload    # flash the release build
```

Log with the macros, never with `Serial` directly, so the release build stays silent:

```cpp
LOG("POST /panic/start -> %d\n", status);   // printf-style
LOG_FLUSH();                                  // before deep sleep, so the last lines get out
```

In VS Code the env picker in the PlatformIO status bar (bottom) switches which one the build/upload buttons use.

Or use the PlatformIO toolbar buttons at the bottom of VS Code, which do the same thing.

## Serial monitor

The XIAO ESP32-C6 talks over the chip's built-in USB serial, so **every reset re-enumerates the USB device** and the
COM port disappears for a moment. PlatformIO's monitor reconnects automatically when that happens — as long as it
knows which port to come back to. Auto-detection is unreliable on this board (the port reports Espressif's vendor ID,
not the one in the board definition, and any Bluetooth COM ports compete with it), so pin it:

1. Find the board's port with `pio device list` — it's the `USB VID:PID=303A:1001` entry.
2. Put it in `platformio.local.ini` next to `platformio.ini` (gitignored, merged in via `extra_configs`):

   ```ini
   [env:seeed_xiao_esp32c6]
   upload_port = COM7
   monitor_port = COM7
   ```

Then run the monitor in a terminal **outside** VS Code's task runner if you want it to outlive rebuilds and
uploads — any PowerShell/Windows Terminal window will do:

```bash
pio device monitor      # reconnects by itself after the board resets; Ctrl+C to quit
```

(`pio run -t upload` can't flash while a monitor holds the port — close it first, or let the VS Code task do both
with "Upload and Monitor".)

`monitor_filters = esp32_exception_decoder` in `platformio.ini` turns crash backtraces in the monitor into
file:line references using the current `firmware.elf`.

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
* All other pins are defined in `src/pinout.h`. Panic button on GPIO 0 and the lid's reed switch on GPIO 1 are the
  deep-sleep (ext1) wake sources, both wired active high. The KY-040 rotary encoder's A/B go to GPIO 19/17 and its
  push button (active low, external pull-up) to GPIO 18; a separate back button (active high, external pull-down) is
  on GPIO 20. The 128×64 I2C OLED sits on the board's `SDA`/`SCL` pins and is driven by the OneBitDisplay library.
  The built-in fonts are fixed-width, so a row holds `128 / char width` characters (21 with `FONT_SMALL`); the
  `display` text functions cut anything longer rather than letting the library wrap it over the next row.
* The encoder is decoded with a Gray-code quadrature table in `controls.cpp` (one detent = one full 4-step cycle),
  which is what makes it immune to contact bounce. Don't swap it for a single-edge read plus a `millis()` debounce;
  that was the original jumpy version.
* `lib_ldf_mode = chain` in `platformio.ini` is required for OneBitDisplay to build; see the comment there.
* Pinout and specs: [Seeed wiki](https://wiki.seeedstudio.com/xiao_esp32c6_getting_started/).

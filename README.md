# PanicDisco 🕺

A professional backend developer's "I'm bored let's make something stupid project".

With a workday filled with Claude usage, I've tried to do a lot of the stuff here manually, except for the really boring stuff.

Also, I'm very much a backend developer, and really can't be bothered with frontend, so all the frontend (html/css/js is vibe coded)

Boring stuff includes:
* Tests
* Swagger
* Plumbing like config, blueprints, etc..
* Frontend

## What's here

This is a monorepo of independent Python packages, each with its own `pyproject.toml`
and its own `uv`-managed virtual environment, living under `src/`:

- **`disco_server`** — the Flask app. A track library (upload `.mp3`/`.wav`/`.flac`
  files with a name and cue point, list/edit/delete them), a **web UI** (`/` and
  `/upload` — drag-and-drop uploads, an in-browser player for picking a cue point,
  inline preview/edit/delete), a **JSON API** (`/api/tracks*`, explorable at
  `/apidocs/`), a **Boombox** that plays a track through VLC seeking to its cue
  point, and a **panic button** (`/api/panic/*`) — an extensible hook point where
  registered `PanicAction`s (e.g. starting Boombox playback) all run on trigger and
  all run their stop behavior when it's cleared. This is what runs on the
  ceiling-mounted Raspberry Pi unit (see [PARTLIST.md](PARTLIST.md)).
- **`disco_shared`** — the API contracts both `disco_server` and `disco_client` need
  to agree on: the exact same pydantic models the server serializes responses with
  are what the client deserializes them with, so there's one source of truth for the
  wire format instead of two independently-maintained shapes.
- **`disco_client`** — a thin `requests`-based HTTP wrapper around `disco_server`'s
  JSON API, meant to be consumed by other Python projects (e.g. a future button/panic
  hardware project) without pulling in Flask, VLC, or SQLAlchemy — see
  [`disco_client`](#disco_client) below.

Why split it like this instead of one big package? The hardware/button project this
is ultimately for shouldn't need Flask, VLC, or SQLAlchemy installed just to make an
HTTP call — `disco_client` (and whatever consumes it) stays lightweight by only
depending on `disco_shared` + `requests`.

## Getting started

You'll need Python 3.12+ and [`uv`](https://docs.astral.sh/uv/) (`curl -LsSf
https://astral.sh/uv/install.sh | sh`, or see uv's docs for other install methods).

Each package under `src/` is independent — it gets its own venv, synced from inside
its own directory. `disco_server` and `disco_client` both depend on `disco_shared`
via a local path dependency (`../disco_shared`), so **`disco_shared` must exist as a
sibling directory** wherever either of them is set up — you can't move/copy just
`disco_server` on its own and expect it to resolve.

To get `disco_server` running:

1. Sync its dependencies (this creates `src/disco_server/.venv`, resolving
   `disco_shared` from the sibling directory automatically):
   ```
   cd src/disco_server
   uv sync --extra dev
   ```
2. Initialize the database (creates tables that don't already exist yet; safe to
   re-run):
   ```
   uv run flask --app disco_server init-db
   ```
3. Run the Flask app:
   ```
   uv run flask --app disco_server run
   ```
   The JSON API is ready to go at this point — try `curl localhost:5000/api/tracks`.
   Want the styled web UI too? See [Frontend](#frontend-tailwind-css) below, it's one
   extra step. Want a production-ready server instead of Flask's dev server (e.g. for
   the Raspberry Pi)? See [Deploying disco_server](#deploying-disco_server-to-a-raspberry-pi).

To set up `disco_shared` or `disco_client` on their own (e.g. to work on the client,
or a future hardware project consuming it), the pattern is the same — `cd` into the
package's directory and `uv sync`:
```
cd src/disco_client
uv sync --extra dev
```

## Tests

Each package's own venv is what runs its tests — there's no shared root venv. Run
each from the repo root, via the matching package's venv (so pytest finds `tests/`
and the root `pyproject.toml`'s config):
```
src/disco_server/.venv/bin/python -m pytest tests/integration -v   # disco_server + disco_shared, real SQLite, VLC mocked
src/disco_client/.venv/bin/python -m pytest tests/disco_client -v  # disco_client, HTTP mocked via requests-mock
src/disco_shared/.venv/bin/python -m pytest tests/disco_shared -v  # disco_shared's own models
src/disco_server/.venv/bin/python -m pytest tests/e2e -v           # disco_client against a REAL disco_server, real HTTP
```
The last one needs `disco_server` synced with its `e2e` extra too (`uv sync --extra
dev --extra e2e` — pulls in `disco_client` as a local dependency), since it runs a
real server on a real socket to prove the client and server actually agree on the
wire format, which the mocked `disco_client` suite can't catch on its own (e.g. a
changed route path or header format).

## Frontend (Tailwind CSS)

The UI templates (`src/disco_server/disco_server/templates/`) are styled with
Tailwind CSS. Its source lives in
`src/disco_server/disco_server/assets/css/input.css`; the compiled stylesheet Flask
actually serves (`src/disco_server/disco_server/static/css/tailwind.css`) **is
checked into git**, deliberately — that means the Raspberry Pi deploy never needs
Node.js/npm installed at all, just `git pull`. The tradeoff is that it's on you to
rebuild and commit it after changing a template or the source CSS; nothing enforces
that automatically.

1. Install the Tailwind CLI (Node.js required — this is separate from the Python
   venvs above, and only ever needed on your dev machine, never on the Pi):
   ```
   npm install
   ```
2. Build the stylesheet:
   ```
   npm run build:css
   ```
   Or, while actively editing templates or styles, run it in watch mode so it
   rebuilds on every save:
   ```
   npm run watch:css
   ```
3. Run the Flask app as usual (see [Getting started](#getting-started) above) —
   `templates/*.html` link the compiled file via
   `{{ url_for('static', filename='css/tailwind.css') }}`.
4. **Commit the rebuilt `tailwind.css`** along with whatever template/style change
   prompted it — it won't get picked up on the Pi otherwise, since `git pull` is the
   entire deploy mechanism for it.

One thing to remember: re-run `npm run build:css` (or keep `watch:css` running) any
time you add Tailwind utility classes to a template — the build only picks up
classes it can actually find by scanning `src/disco_server/disco_server/templates`.

## `disco_client`

A minimal example, using the `DiscoClient` facade:
```python
from disco_client import DiscoClient

client = DiscoClient("http://disco-server.local:5000")
for track in client.tracks.list_tracks():
    print(track.id, track.name)
```
See `tests/manual/list_tracks_client.py` for a runnable version of this — it expects
a `disco_server` instance already running (see [Getting started](#getting-started)).

## Deploying `disco_server` to a Raspberry Pi

`disco_server` is the piece that runs on the actual ceiling-mounted unit (audio +
lights, see [PARTLIST.md](PARTLIST.md)) — `disco_shared` and `disco_client` don't
need to be deployed there; they're for whatever separately runs the panic-button
hardware project.

### 1. Get the code onto the Pi

```bash
sudo apt update
sudo apt install -y git
git clone <this-repo-url>
```
A full clone is simplest and makes future updates a `git pull` — but if you'd rather
copy files directly instead of cloning, remember `disco_server` needs `disco_shared`
present as a sibling directory (`src/disco_shared/` next to `src/disco_server/`) for
its path dependency to resolve; you cannot copy `src/disco_server/` alone.

This assumes a 64-bit Raspberry Pi OS (Bookworm or newer). On a 32-bit OS, some
dependencies (`pydantic-core`, `SQLAlchemy`) may not have prebuilt wheels available
and would need to compile from source on-device, which is slow and needs build
tools installed — using 64-bit OS is strongly recommended.

### 2. Run the install script

```bash
./scripts/install-disco-server.sh
```
Installs the remaining system dependencies (`vlc`, for the `libvlc` `python-vlc`
needs at runtime), installs `uv` if it isn't already, syncs `disco_shared` and
`disco_server`, initializes the database, and installs+starts a systemd service
(`disco-server`) so it survives reboots and restarts on crash. Safe to re-run —
every step is idempotent. If the Pi's system Python is older than 3.12 (common on
Raspberry Pi OS), don't worry about it — `uv sync` transparently downloads and uses
a matching Python 3.12 build on its own.

Notably, this doesn't touch Node.js/npm at all — the Tailwind stylesheet is a
committed build artifact (see [Frontend](#frontend-tailwind-css) above), so it just
comes along with the code via `git clone`/`git pull`. The Pi never needs a Node
toolchain installed.

Check it's up with `systemctl status disco-server` and `curl localhost:5000/api/tracks`.

If you'd rather run the steps by hand instead of using the script (or need to adapt
them — e.g. a different service user), see what the script actually does:
[`scripts/install-disco-server.sh`](scripts/install-disco-server.sh).

### 3. Why Waitress, not `flask run` or Gunicorn

Flask's own dev server explicitly warns it isn't for production use, so the install
script sets up [Waitress](https://docs.pylonsproject.org/projects/waitress/) instead
(`waitress-serve --call disco_server:create_app`, run by the systemd service). It's
used specifically because it's **single-process, thread-based only** — no
multi-worker-process model at all. That matters here: `disco_server` caches its
`Boombox` (the one VLC player talking to the Pi's audio output), `TrackLibrary`, and
registered panic actions on `current_app.extensions`, which is per-process state. A
multi-worker server (like Gunicorn's default) would give each worker its *own*
separate Boombox/VLC instance — a "load track" request could land on one worker and
a "play" request on another, breaking playback state or fighting over the same
physical audio device. Waitress sidesteps this by construction; if you use Gunicorn
instead, you must pin it to `--workers 1` (threads are fine, e.g. `--threads 4`) to
get the same single-process guarantee.

### 4. Redeploying updates

```bash
./scripts/redeploy-disco-server.sh
```
Pulls the latest commit (fast-forward only — it refuses if there are local
uncommitted changes, so it won't silently clobber anything), re-syncs
`disco_shared` and `disco_server`, restarts the `disco-server` systemd service, and
polls `/api/tracks` for up to 10s to confirm it actually came back up. The `git
pull` alone brings any updated Tailwind stylesheet too, since it's committed rather
than built on the Pi. Needs the one-time setup from steps 1–2 above already done
(uv installed, the service unit in place, passwordless — or interactive — `sudo`
for `systemctl restart`).

If you'd rather run the steps by hand:
```bash
cd PanicDisco
git pull
cd src/disco_shared && uv sync   # if disco_shared changed
cd ../disco_server && uv sync --extra deploy
sudo systemctl restart disco-server
```
Never delete or overwrite `src/disco_server/instance/` when redeploying — that's
where the sqlite database and uploaded audio files actually live. Back it up before
any change you're not sure about.

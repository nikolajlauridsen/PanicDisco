# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

PanicDisco / `disco_server`: a Flask-based server for controlling a track library and audio playback (via VLC). The Flask app itself is currently just a stub (`/hello` route) — the real logic lives in the `core` layer (database, models, services) and is exercised today through manual scripts and integration tests rather than HTTP endpoints.

## Setup and commands

```bash
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
pip install -e .          # installs disco_server in editable mode from src/
```

Initialize the database (creates tables that don't already exist yet; safe to re-run):
```bash
flask --app disco_server init-db
```

Run the Flask app:
```bash
flask --app disco_server run
```

Run tests:
```bash
python3 -m pytest tests/integration -v
```
Run a single test: `python3 -m pytest tests/integration/test_track_library.py::test_create_track_persists_to_database -v`

Manual/exploratory scripts (need a real audio file and a real VLC install; not run in CI). Both call `create_app()` and use `app.database`, so they read/write the same SQLite file the Flask app would use (`<instance_path>/disco_server.sqlite3` by default):
```bash
python tests/manual/seed_database.py   # calls app.database.init_db() itself, prompts for a directory, seeds app.database with its .mp3 files
python tests/manual/boombox.py         # lists tracks in app.database, plays a chosen one via Boombox — run init-db or seed_database.py first
```

## Architecture

- `src/disco_server/__init__.py` — `create_app(test_config=None)` Flask factory. Loads config with `DATABASE_PATH` defaulting to `<instance_path>/disco_server.sqlite3` (overridable via `instance/config.py`, or by passing a `test_config` dict — the flaskr-tutorial pattern), then builds `app.database` (a `Database` instance) from it. Table creation is *not* automatic — it's exposed as the `flask init-db` CLI command (`app.cli.command('init-db')`), following the same flaskr-tutorial pattern, so schema initialization stays an explicit, deliberate action rather than something that runs on every app start/worker. This is where routes/blueprints will be wired up as the HTTP API grows; they should reuse `app.database`/`current_app.database` rather than constructing their own `Database`.
- `src/disco_server/core/models/track.py` — `Track`: a single SQLAlchemy `DeclarativeBase` model (`Base` in `dtos/base.py`) that doubles as both the domain object and the persisted row (no separate DTO/domain mapping — see commit "Don't map back and forth between dto and domain model").
- `src/disco_server/core/database/database.py` — `Database` wraps a SQLAlchemy engine/scoped session against a SQLite file and exposes CRUD primitives (`add_track`, `remove_track`, `save_changes`, `get_tracks`). `db_path` is a required constructor arg (framework-agnostic — no default); the default `DATABASE_PATH` used at runtime lives in Flask config via `create_app`, not in `Database` itself.
- `src/disco_server/core/services/track_library.py` — `TrackLibrary` is the in-memory-plus-database layer application code should use instead of `Database` directly. It loads all tracks into a list on construction and mutates both the list and the database together on create/update/delete. Because it caches tracks in memory at construction time, a second `TrackLibrary` instance must be built against the same `Database` to observe changes made elsewhere (see `reload()` helper in the integration tests).
  - All lookups/mutations key off `id` (`get_track`, `update_track`) or object identity (`delete_track` matches by object identity, not by field equality) — names are not unique, so id-based matching avoids ambiguity between duplicate-named tracks.
- `src/disco_server/core/services/boombox.py` — `Boombox` wraps a single `vlc.MediaPlayer` for one loaded `Track` at a time (`load_track` → `play`/`pause`/`resume`/`stop`). Playback methods raise `RuntimeError` via `_ensure_loaded()` if called before `load_track`. If a track has `cue_time` set, `play()` seeks to it (in seconds, converted to ms for VLC) after starting playback.

## Testing conventions

- Integration tests (`tests/integration/`) run against a real SQLite database backed by a per-test temp file (`conftest.py`'s `db_path`/`database`/`library` fixtures), not a mock — persistence is asserted by constructing a second `TrackLibrary`/`Database` from the same file and reading state back.
- `test_app.py` covers `create_app`'s config wiring and the `init-db` CLI command, using a `test_config` dict (overriding `DATABASE_PATH` to a temp path) rather than exercising the parameterless default, which would write a real file under `src/instance/`. The CLI command is invoked via `app.test_cli_runner().invoke(...)`.
- `tests/manual/` scripts are not part of the automated suite; they require real hardware/audio files and are meant to be run manually against a real VLC install.

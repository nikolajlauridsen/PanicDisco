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

- **A track library** — upload `.mp3`/`.wav`/`.flac` files with a name and a cue
  point, list/edit/delete them later.
- **A web UI** (`/` and `/upload`) — drag-and-drop uploads, an in-browser player for
  picking a cue point, inline preview/edit/delete on the track list. No page reloads,
  just plain JS and Tailwind CSS.
- **A JSON API** (`/api/tracks*`) — everything the UI does, scriptable. Explore it at
  `/apidocs/` once the app is running.
- **Boombox** — plays a chosen track through VLC, seeking to its cue point.

## Getting started

You'll need Python 3.12+. Here's the fastest path to a running app:

1. Create and activate a virtual environment:
   ```
   python3 -m venv env
   source env/bin/activate
   ```
2. Install the runtime dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install `disco_server` itself in editable mode, so it's importable from anywhere
   (manual test scripts, a REPL, etc.) and edits to `src/disco_server` take effect
   immediately without reinstalling:
   ```
   pip install -e .
   ```
4. Initialize the database (creates tables that don't already exist yet; safe to
   re-run):
   ```
   flask --app disco_server init-db
   ```
5. Run the Flask app:
   ```
   flask --app disco_server run
   ```
   The JSON API is ready to go at this point — try `curl localhost:5000/api/tracks`.
   Want the styled web UI too? See [Frontend](#frontend-tailwind-css) below, it's one
   extra step.

## Tests

```
python3 -m pytest tests/integration -v
```

## Frontend (Tailwind CSS)

The UI templates (`src/disco_server/templates/`) are styled with Tailwind CSS. Its
source lives in `src/disco_server/assets/css/input.css`; the compiled stylesheet
Flask actually serves (`src/disco_server/static/css/tailwind.css`) is a generated
build artifact and isn't checked into git, so it needs to be built at least once
before the UI looks like anything more than unstyled HTML.

1. Install the Tailwind CLI (Node.js required — this is separate from the Python
   venv above):
   ```
   npm install
   ```
2. Build the stylesheet once:
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

One thing to remember: re-run `npm run build:css` (or keep `watch:css` running) any
time you add Tailwind utility classes to a template — the build only picks up
classes it can actually find by scanning `src/disco_server/templates`.

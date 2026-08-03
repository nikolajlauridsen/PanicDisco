# PanicDisco
Panic at the disco! 

## Getting started

1. Create and activate a virtual environment:
   ```
   python3 -m venv env
   source env/bin/activate
   ```
2. Install the runtime dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Install `disco_server` itself in editable mode, so it's importable from anywhere (manual test scripts, a REPL, etc.) and edits to `src/disco_server` take effect immediately without reinstalling:
   ```
   pip install -e .
   ```
4. Initialize the database (creates tables that don't already exist yet; safe to re-run):
   ```
   flask --app disco_server init-db
   ```
5. Run the Flask app:
   ```
   flask --app disco_server run
   ```
6. Manual/exploratory test scripts live under `tests/manual/` (e.g. `tests/manual/boombox.py`). Run them directly with the venv active:
   ```
   python tests/manual/boombox.py
   ```
### Tests

Run tests with 

```
python3 -m pytest tests/integration -v
```

### Frontend (Tailwind CSS)

The UI templates (`src/disco_server/templates/`) are styled with Tailwind CSS.
Tailwind's source lives in `src/disco_server/assets/css/input.css`; the compiled
stylesheet Flask actually serves (`src/disco_server/static/css/tailwind.css`) is a
generated build artifact and isn't checked into git, so it must be built at least
once before the UI will be styled.

1. Install the Tailwind CLI (Node.js required, not part of the Python venv):
   ```
   npm install
   ```
2. Build the stylesheet once:
   ```
   npm run build:css
   ```
   Or, while actively editing templates/styles, run it in watch mode so it
   rebuilds on every save:
   ```
   npm run watch:css
   ```
3. Run the Flask app as usual (see above) — `templates/*.html` link the compiled
   file via `{{ url_for('static', filename='css/tailwind.css') }}`.

Re-run `npm run build:css` (or keep `watch:css` running) any time you add Tailwind
utility classes to a template — the build only includes classes it can find by
scanning `src/disco_server/templates`.
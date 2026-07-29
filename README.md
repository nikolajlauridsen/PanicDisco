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
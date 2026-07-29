---
name: update-swagger-docs
description: Keeps disco_server's flasgger-generated Swagger/OpenAPI docs in sync with the actual code — the `definitions` dict in src/disco_server/web/swagger_template.py and the YAML docstrings in src/disco_server/blueprints/*.py. Use this any time a Flask route is added, removed, or has its request/response shape changed in a blueprint file, any time a pydantic view model or dataclass used as a request/response shape (e.g. TrackDetails, TrackUpdate, Error) gains, loses, renames, or retypes a field, or whenever the user asks to "update the swagger docs", "sync the API spec", "regenerate the OpenAPI definitions", or anything about keeping "the endpoint docs" or "the API docs" current — even if they don't say flasgger or Swagger by name. Also worth running as a check after any change that touches blueprints/ or web/view_models/, since stale docs are easy to miss and won't cause test failures on their own.
---

# Updating disco_server's Swagger docs

disco_server documents its `/api/tracks*` routes with flasgger: a hand-maintained
`definitions` dict in `src/disco_server/web/swagger_template.py`, and a YAML block in
each route's docstring in `src/disco_server/blueprints/*.py` that `$ref`s those
definitions. Nothing regenerates these automatically — they drift the moment a route
or model changes underneath them, and a stale doc doesn't fail any test on its own
(the app runs fine, `/apispec_1.json` still returns 200, it's just wrong). This skill
is the deliberate step that keeps them honest.

## 1. Work out what changed

Look at what you (or the user) just edited — `git diff`, or the routes/models named in
the request. You're looking for two things:
- **Routes** in `src/disco_server/blueprints/*.py`: added, removed, or a changed set of
  path params / request body / response shape / status codes.
- **View models** in `src/disco_server/web/view_models/{request_models,response_models}/*.py`:
  a pydantic `BaseModel` or dataclass gaining, losing, renaming, or retyping a field.

A model change and a route change often arrive together (add a field to `TrackUpdate`,
wire it into `update_track`) — handle both in the same pass so the docs and the route
land in the same state.

## 2. Regenerate the definitions — don't hand-write them

Run the bundled script against every model that changed:

```
source env/bin/activate && python .claude/skills/update-swagger-docs/scripts/generate_definitions.py \
  disco_server.web.view_models.response_models.track_details.TrackDetails:serialization \
  disco_server.web.view_models.request_models.track_update.TrackUpdate \
  disco_server.web.view_models.response_models.error.Error
```

It prints a JSON fragment ready to merge into `definitions`. Hand-writing these by eye
is where mistakes creep in — Swagger 2.0 predates JSON Schema's `type: null`, so a
nullable field (like `TrackDetails.cue_point`) has to become `x-nullable: true` instead
of an `anyOf`, and it's an easy thing to get subtly wrong or forget when a new nullable
field shows up.

**Pick validation vs serialization deliberately, per model — this is the part most
worth double-checking, not the part to rubber-stamp:**
- A model used to parse an incoming request body (like `TrackUpdate` in `update_track`)
  should use `:validation` (the default) — it reflects what keys the client must send.
- A model used to shape an outgoing response (like `TrackDetails` in `get_track`) should
  use `:serialization` — it reflects what `model_dump(by_alias=True)` actually emits.
  These can genuinely disagree: `TrackDetails.cue_point` has a `validation_alias='cue_time'`
  (for reading off the `Track` domain object) but serializes back out as `cue_point`, so
  the wrong mode would document a field name that never appears in a real response.
  If you're ever unsure which mode is right for a given model, run both and read the
  actual route code to see whether it's the input side (`model_validate`) or the output
  side (`jsonify(...)`) of that model that's being documented.

Dataclasses (like `Error`) aren't pydantic, so the script introspects their type hints
directly instead — pass them with no mode suffix.

## 3. Merge into `swagger_template.py`

Open `src/disco_server/web/swagger_template.py` and replace only the entries for the
models that changed inside the `definitions` dict returned by `build_swagger_template()`.
Leave every untouched model's entry exactly as it was — a full rewrite makes the diff
noisy and risks silently reverting an intentional tweak to an unrelated definition.

## 4. Update the route docstrings

For each added or changed route in the blueprint file, add or update its flasgger YAML
docstring block. Match the house style already in `tracks.py`: a `tags` list, `parameters`
for path/body params, and a `responses` map keyed by status code that references schemas
via `$ref: '#/definitions/<ModelName>'` rather than repeating the shape inline. A removed
route's docstring block goes with it; a renamed field needs its parameter/property
references updated to match.

## 5. Verify — don't just trust that it looks right

Flasgger silently drops a docstring's YAML block if it's malformed rather than raising an
error, so a green test suite is necessary but not sufficient proof the block itself parsed.
Check both:

```
source env/bin/activate && python3 -m pytest tests/integration -v
```

and that the spec itself reflects your changes, using the Flask test client rather than a
live server (matches how `tests/integration/test_swagger.py` already does it — faster, no
port conflicts):

```python
from disco_server import create_app
app = create_app({"DATABASE_PATH": "/tmp/verify.sqlite3"})
resp = app.test_client().get("/apispec_1.json")
print(resp.status_code, resp.get_json()["paths"].keys())
```

Confirm every path/method you touched shows up, and that any `$ref` you added points at a
definition that actually exists in the merged dict (a dangling `$ref` won't error anywhere
in this pipeline — flasgger and the test client are both happy to serve a spec with a
broken reference).

If this added a genuinely new route or model rather than modifying an existing one,
consider whether `tests/integration/test_swagger.py` should gain an assertion for it,
following the pattern of its existing checks — use judgment here, since not every change
needs a new hardcoded assertion if it doesn't add real coverage beyond what the docs
already show.

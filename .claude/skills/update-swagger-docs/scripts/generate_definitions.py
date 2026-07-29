"""Generate Swagger 2.0 `definitions` fragments from disco_server view models.

Usage:
    python generate_definitions.py <dotted.path.to.Model>[:mode] [...]

Each argument is a dotted import path to a pydantic BaseModel or a plain
dataclass used as a request/response shape somewhere in disco_server, e.g.

    disco_server.web.view_models.response_models.track_details.TrackDetails:serialization
    disco_server.web.view_models.request_models.track_update.TrackUpdate
    disco_server.web.view_models.response_models.error.Error

Prints a JSON object mapping model name -> Swagger 2.0 schema to stdout.
Merge the relevant entries into the `definitions` dict returned by
build_swagger_template() in src/disco_server/web/swagger_template.py.

Pydantic models take an optional `:validation` or `:serialization` suffix:
- `:serialization` (use for RESPONSE models) matches the keys that actually
  appear in a JSON response, i.e. what model_dump(by_alias=True) produces.
- `:validation` (the default, use for REQUEST models) matches the keys a
  client must send for model_validate() to accept, honoring
  `validation_alias` where the model uses aliasing.
These two can genuinely differ (see TrackDetails.cue_point, which has a
`validation_alias='cue_time'` for reading off the domain object but
serializes back out as `cue_point`) — always pass the mode matching how the
route actually uses the model, not just the default.

Dataclasses (e.g. Error) aren't pydantic, so there's no schema API to call:
this script introspects type hints directly instead.
"""
import argparse
import dataclasses
import importlib
import json
import sys
import typing

from pydantic import BaseModel

PY_TYPE_TO_SCHEMA_TYPE = {
    str: 'string',
    int: 'integer',
    float: 'number',
    bool: 'boolean',
}


def load_class(dotted_path):
    module_path, _, class_name = dotted_path.rpartition('.')
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def clean(schema):
    """Strip pydantic's per-field `title` noise and fold
    `anyOf: [X, {type: null}]` into Swagger 2.0's `x-nullable` extension
    (Swagger 2.0 predates JSON Schema's `type: null` and has no equivalent)."""
    schema.pop('title', None)
    if 'anyOf' in schema:
        variants = [v for v in schema['anyOf'] if v.get('type') != 'null']
        is_nullable = len(variants) != len(schema['anyOf'])
        if len(variants) == 1:
            merged = {**schema, **variants[0]}
            merged.pop('anyOf', None)
            if is_nullable:
                merged['x-nullable'] = True
            return clean(merged)
    if schema.get('type') == 'object' and 'properties' in schema:
        schema['properties'] = {k: clean(v) for k, v in schema['properties'].items()}
    if schema.get('type') == 'array' and 'items' in schema:
        schema['items'] = clean(schema['items'])
    return schema


def pydantic_definitions(model, mode):
    raw = model.model_json_schema(mode=mode, ref_template='#/definitions/{model}')
    nested = raw.pop('$defs', {})
    definitions = {model.__name__: clean(raw)}
    for name, sub_schema in nested.items():
        definitions[name] = clean(sub_schema)
    return definitions


def dataclass_schema(cls):
    hints = typing.get_type_hints(cls)
    properties = {}
    required = []
    for field in dataclasses.fields(cls):
        hint = hints[field.name]
        origin = typing.get_origin(hint)
        args = typing.get_args(hint)
        is_optional = origin is typing.Union and type(None) in args
        base_type = next((a for a in args if a is not type(None)), hint) if is_optional else hint
        schema_type = PY_TYPE_TO_SCHEMA_TYPE.get(base_type, 'string')
        prop = {'type': schema_type}
        if is_optional:
            prop['x-nullable'] = True
        properties[field.name] = prop
        has_default = field.default is not dataclasses.MISSING or field.default_factory is not dataclasses.MISSING
        if not has_default and not is_optional:
            required.append(field.name)
    schema = {'type': 'object', 'properties': properties}
    if required:
        schema['required'] = required
    return {cls.__name__: schema}


def build_definitions(specs):
    definitions = {}
    for spec in specs:
        dotted_path, sep, mode = spec.rpartition(':')
        if not (sep and mode in ('validation', 'serialization')):
            dotted_path, mode = spec, 'validation'
        cls = load_class(dotted_path)
        if issubclass(cls, BaseModel):
            definitions.update(pydantic_definitions(cls, mode))
        elif dataclasses.is_dataclass(cls):
            definitions.update(dataclass_schema(cls))
        else:
            raise TypeError(f"{dotted_path} is neither a pydantic BaseModel nor a dataclass")
    return definitions


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('models', nargs='+', help="e.g. pkg.module.TrackDetails:serialization")
    args = parser.parse_args()
    json.dump(build_definitions(args.models), sys.stdout, indent=2)
    sys.stdout.write('\n')


if __name__ == '__main__':
    main()

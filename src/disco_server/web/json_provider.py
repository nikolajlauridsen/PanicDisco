from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel


class PydanticJSONProvider(DefaultJSONProvider):
    """JSON provider that also knows how to serialize pydantic view models."""

    @staticmethod
    def default(o):
        if isinstance(o, BaseModel):
            return o.model_dump(mode='json', by_alias=True)
        return DefaultJSONProvider.default(o)

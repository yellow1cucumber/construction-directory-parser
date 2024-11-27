from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        return super().default(o)
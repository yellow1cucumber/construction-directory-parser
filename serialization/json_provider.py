from flask.json.provider import DefaultJSONProvider
from pydantic import BaseModel


class CustomJSONProvider(DefaultJSONProvider):
    def default(self, o):
        if isinstance(o, BaseModel):
            return o.model_dump()
        if isinstance(o, bytes):
            return o.decode('latin1')
        return super().default(o)

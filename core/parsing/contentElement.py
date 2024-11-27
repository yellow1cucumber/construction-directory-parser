from pydantic import BaseModel, Field


class ContentElement(BaseModel):
    type: str
    content: str
    attributes: dict = Field(default_factory=dict)

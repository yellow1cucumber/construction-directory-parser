from pydantic import BaseModel, ConfigDict
from typing import List
from core.parsing.contentElement import ContentElement

class PageContent(BaseModel):
    elements: List[ContentElement]
    model_config = ConfigDict(arbitrary_types_allowed=True)

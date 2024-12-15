from pydantic import BaseModel, ConfigDict
from typing import List
from core.content_parsing.contentElement import ContentElement

class PageContent(BaseModel):
    """
    Represents the structured content of a web page.

    Attributes:
        elements (List[ContentElement]): A list of content elements extracted from the page.
        model_config (ConfigDict): Configuration for Pydantic to allow arbitrary types in the model.
    """
    elements: List[ContentElement]
    model_config = ConfigDict(arbitrary_types_allowed=True)

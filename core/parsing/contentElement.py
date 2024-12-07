from pydantic import BaseModel, Field

class ContentElement(BaseModel):
    """
    Represents a single content element extracted from a web page.

    Attributes:
        type (str): The type of the content element (e.g., "heading", "paragraph", "image").
        content (str): The main content or data associated with the element.
        attributes (dict): Additional attributes related to the content element (e.g., metadata, formatting details).
    """
    type: str
    content: str
    attributes: dict = Field(default_factory=dict)

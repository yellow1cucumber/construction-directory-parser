from typing import List
from pydantic import BaseModel
from core.extraction.category import Category

class SiteMap(BaseModel):
    """
    Represents a sitemap structure for a website.

    Attributes:
        root_url (str): The root URL of the website.
        categories (List[Category]): A list of categories that form the sitemap's hierarchy.
    """

    root_url: str
    categories: List[Category]

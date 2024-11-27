from typing import List

from pydantic import BaseModel

from core.extraction.category import Category


class SiteMap(BaseModel):
    """
    Класс для представления карты сайта.
    """
    root_url: str
    categories: List[Category]
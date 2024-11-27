from typing import List

from pydantic import BaseModel, ConfigDict

from core.extraction.article import Article


class Category(BaseModel):
    """
    Класс для представления категории, которая может содержать подкатегории и статьи.
    """
    name: str
    url: str
    subcategories: List['Category']
    articles: List[Article]

    def __hash__(self):
        return hash((
            self.name,
            self.url,
            self.subcategories,
            self.articles
        ))

    def __eq__(self, other):
        if isinstance(other, Category):
            return (self.name == other.name and
                    self.url == other.url and
                    self.subcategories.__len__() == other.subcategories.__len__() and
                    self.articles.__len__() == other.articles.__len__())
        return False

    model_config = ConfigDict(frozen=True)
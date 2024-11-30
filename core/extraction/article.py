from pydantic import BaseModel, ConfigDict


class Article(BaseModel):
    """
    Класс для представления статьи.
    """
    title: str
    url: str

    def __hash__(self):
        return hash((self.title, self.url))

    def __eq__(self, other):
        if isinstance(other, Article):
            return self.title == other.title and self.url == other.url
        return False
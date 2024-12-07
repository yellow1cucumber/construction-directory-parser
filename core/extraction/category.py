from typing import List
from pydantic import BaseModel
from core.extraction.article import Article


class Category(BaseModel):
    """
    Represents a category that may contain subcategories and articles.

    Attributes:
        name (str): The name of the category.
        url (str): The URL of the category.
        subcategories (List[Category]): A list of subcategories within this category.
        articles (List[Article]): A list of articles associated with this category.
    """

    name: str
    url: str
    subcategories: List['Category']
    articles: List[Article]

    def __hash__(self):
        """
        Computes a hash value for the Category instance.

        The hash is based on the category's name, URL, subcategories, and articles.
        This allows the Category to be used in hashable collections like sets and as dictionary keys.

        Returns:
            int: The hash value of the Category.
        """
        return hash((
            self.name,
            self.url,
            self.subcategories,
            self.articles
        ))

    def __eq__(self, other):
        """
        Compares two Category instances for equality.

        Two categories are considered equal if:
        - Their names are the same.
        - Their URLs are the same.
        - They have the same number of subcategories.
        - They have the same number of articles.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is a Category with matching attributes, False otherwise.
        """
        if isinstance(other, Category):
            return (self.name == other.name and
                    self.url == other.url and
                    len(self.subcategories) == len(other.subcategories) and
                    len(self.articles) == len(other.articles))
        return False

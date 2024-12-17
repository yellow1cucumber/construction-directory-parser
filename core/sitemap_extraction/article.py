from pydantic import BaseModel


class Article(BaseModel):
    """
    Represents an article with a title and URL.

    Attributes:
        title (str): The title of the article.
        url (str): The URL of the article.
    """

    title: str
    url: str
    html: str | bytes

    def __hash__(self):
        """
        Computes a hash value for the Article instance.

        The hash is based on the title and URL, ensuring that two articles
        with the same title and URL produce the same hash.

        Returns:
            int: The hash value of the Article.
        """
        return hash((self.title, self.url))

    def __eq__(self, other):
        """
        Compares two Article instances for equality.

        Two Article instances are considered equal if their titles and URLs match.

        Args:
            other (object): The object to compare against.

        Returns:
            bool: True if the other object is an Article with the same title and URL, False otherwise.
        """
        if isinstance(other, Article):
            return self.title == other.title and self.url == other.url
        return False

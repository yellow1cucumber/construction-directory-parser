from pathlib import Path
from pydantic import BaseModel

from core.sitemap_extraction.category import Category
from core.sitemap_extraction.sitemap import SiteMap
from core.sitemap_extraction.article import Article

from core.content_parsing.content_parser import ContentParser


class ArticleParser:
    """
    Parses articles and categories from a `SiteMap` object and exports the data to a specified directory.

    Attributes:
        root_url (str): The root URL of the site being processed.
        categories (List[Category]): A list of categories to process.

    Methods:
        process(export_dir: str):
            Parse all categories and articles and saves the data to the specified directory.

        process_category(category: Category, parent_path: Path):
            Recursively parse a category and its subcategories, exporting their data.

        process_article(article: Article, save_path: Path):
            Parse an individual article, parsing its content and saving it as a JSON file.

        sanitize_filename(name: str) -> str:
            Sanitizes a string to make it safe for use as a file name.

        save_to_json(data: BaseModel, file_path: Path) -> None:
            Saves a Pydantic model as a JSON file to the specified path.
    """

    def __init__(self, site_map: SiteMap):
        """
        Initializes the ArticleParser with a `SiteMap` object.

        Args:
            site_map (SiteMap): The sitemap containing the root URL and categories to process.
        """
        self.root_url = site_map.root_url
        self.categories = site_map.categories

    def process(self, export_dir: str):
        """
        Parses all categories and articles in the sitemap, saving them to the specified directory.

        Args:
            export_dir (str): The directory where processed data will be saved.
        """
        export_path = Path(export_dir)
        for category in self.categories:
            self.process_category(category, parent_path=export_path)

    def process_category(self, category: Category, parent_path: Path):
        """
        Recursively parses a category and its subcategories, exporting their data to the directory.

        Args:
            category (Category): The category to process.
            parent_path (Path): The directory where the category's data will be saved.
        """
        category_name = self.sanitize_filename(category.name)
        current_path = parent_path / category_name
        current_path.mkdir(parents=True, exist_ok=True)

        subcategories = category.subcategories or []
        articles = category.articles or []

        # Process articles in the current category
        for article in articles:
            self.process_article(article, current_path)

        # Recursively process subcategories
        for subcategory in subcategories:
            self.process_category(subcategory, current_path)

        # If the category has no articles or subcategories, treat it as an article
        if not articles and not subcategories:
            category_as_article = Article(title=category.name, url=category.url)
            self.process_article(category_as_article, current_path)

    def process_article(self, article: Article, save_path: Path):
        """
        Parse an individual article, parsing its content and saving it as a JSON file.

        Args:
            article (Article): The article to process.
            save_path (Path): The directory where the article's data will be saved.

        Raises:
            ValueError: If the article's content cannot be parsed.
        """
        article_title = self.sanitize_filename(article.title)
        article_url = article.url

        # Parse the article's content
        try:
            parser = ContentParser(article_url, 'div.page_text')
            article.html = parser.parse_and_get_pure_html()
            page_content = parser.parse()
        except Exception as e:
            raise ValueError(f"Container with selector 'page_text' not found by url= {article_url}")

        file_path = save_path / f"{article_title}.json"
        self.save_to_json(page_content, file_path)

    def sanitize_filename(self, name: str) -> str:
        """
        Sanitizes a string to make it safe for use as a file name.

        Replaces invalid characters with underscores.

        Args:
            name (str): The string to sanitize.

        Returns:
            str: A sanitized string safe for use as a file name.
        """
        return "".join(c if c.isalnum() or c in ' _-' else '_' for c in name).strip()

    def save_to_json(self, data: BaseModel, file_path: Path) -> None:
        """
        Saves a Pydantic model as a JSON file to the specified path.

        Args:
            data (BaseModel): The Pydantic model to save.
            file_path (Path): The path where the JSON file will be saved.

        Raises:
            Exception: If the file cannot be saved.
        """
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open('w', encoding='utf-8') as f:
                f.write(data.model_dump_json())
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")

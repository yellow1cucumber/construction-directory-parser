from pathlib import Path

from pydantic import BaseModel

from core.extraction.category import Category
from core.extraction.sitemap import SiteMap
from core.extraction.article import Article
from core.parsing.content_parser import ContentParser
from core.parsing.pages_cache import PagesCache


class ArticleProcessor:
    def __init__(self, site_map: SiteMap, cache: PagesCache):
        self.root_url = site_map.root_url
        self.categories = site_map.categories
        self.pages_cache = cache

    def process(self, export_dir: str):
        export_path = Path(export_dir)
        for category in self.categories:
            self.process_category(category, parent_path=export_path)

    def process_category(self, category: Category, parent_path: Path):
        category_name = self.sanitize_filename(category.name)
        current_path = parent_path / category_name
        current_path.mkdir(parents=True, exist_ok=True)

        subcategories = category.subcategories or []
        articles = category.articles or []

        # Обрабатываем статьи в текущей категории
        for article in articles:
            self.process_article(article, current_path)

        # Рекурсивно обрабатываем подкатегории
        for subcategory in subcategories:
            self.process_category(subcategory, current_path)

        # Если категория пуста, то скорее всего она является статьей
        if not articles and not subcategories:
            category_as_article = Article(title=category.name, url=category.url)
            self.process_article(category_as_article, current_path)

    def process_article(self, article: Article, save_path: Path):
        article_title = self.sanitize_filename(article.title)
        article_url = article.url

        # Парсим содержимое статьи
        try:
            parser = ContentParser(article_url, 'div.page_text')
            page_content = parser.parse()
        except Exception as e:
            raise ValueError(f"Container with selector 'page_text' not found by url= {article_url}")

        file_path = save_path / f"{article_title}.json"
        self.save_to_json(page_content, file_path)

        # Сохраняем путь в POSIX-формате для кроссплатформенности
        self.pages_cache.save(article, file_path.as_posix())

    def sanitize_filename(self, name: str) -> str:
        # Заменяем недопустимые символы на "_"
        return "".join(c if c.isalnum() or c in ' _-' else '_' for c in name).strip()

    def save_to_json(self, data: BaseModel, file_path: Path) -> None:
        """Saves data to json"""
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            with file_path.open('w', encoding='utf-8') as f:
                f.write(data.model_dump_json())
        except Exception as e:
            print(f"Error saving file {file_path}: {e}")

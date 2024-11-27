import os
import requests

from core.extraction.category import Category
from core.extraction.sitemap import SiteMap
from core.parsing.contentParser import ContentParser
from core.extraction.article import Article
from core.parsing.pages_cache import PagesCache


class ArticleProcessor:
    def __init__(self, site_map: SiteMap, cache: PagesCache):
        self.root_url = site_map.root_url
        self.categories = site_map.categories
        self.parser = ContentParser()
        self.pages_cache = cache

    def process(self, export_dir: str):
        for category in self.categories:
            self.process_category(category, parent_path=export_dir)

    def process_category(self, category: Category, parent_path: str):
        category_name = self.sanitize_filename(category.name)
        current_path = os.path.join(parent_path, category_name)
        os.makedirs(current_path, exist_ok=True)

        subcategories = category.subcategories
        articles = category.articles

        if not subcategories and not articles:
            # Обрабатываем категорию как статью
            self.process_article(Article(title=category_name, url=category.url), current_path)
        else:
            # Рекурсивно обрабатываем подкатегории
            for subcategory in subcategories:
                self.process_category(subcategory, current_path)
            # Обрабатываем статьи в текущей категории
            for article in articles:
                self.process_article(article, current_path)

    def process_article(self, article: Article, save_path: str):
        article_title = self.sanitize_filename(article.title)
        article_url = article.url
        print(f"Processing article: {article_title}")

        # Получаем HTML содержимое статьи
        html_content = self.fetch_content(article_url)

        # Парсим содержимое статьи
        page_content = self.parser.parse_content(html_content, container_class='page_text')  # Замените на актуальный класс контейнера

        # Сохраняем распарсенное содержимое в JSON-файл
        file_path = os.path.join(save_path, f"{article_title}.json")
        self.parser.save_to_json(page_content, file_path)
        self.pages_cache.save(article, file_path)


    def fetch_content(self, url: str) -> str:
        response = requests.get(url)
        response.raise_for_status()
        return response.text

    def sanitize_filename(self, name: str) -> str:
        return "".join(c if c.isalnum() or c in ' _-' else '_' for c in name).strip()

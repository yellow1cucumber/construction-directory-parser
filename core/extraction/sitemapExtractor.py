import json
from urllib.parse import urljoin
from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from core.extraction.category import Category
from core.extraction.article import Article
from core.extraction.sitemap import SiteMap


class ExtractorOptions(BaseModel):
    """
    Модель для хранения настроек парсера.
    """
    root_url: str  # Корневой URL для начала обхода
    excluded_urls: list[str]  # Список URL, которые нужно игнорировать
    category_tag: str  # HTML-тег для категорий
    category_selectors: List[str]  # Список CSS-селекторов для категорий
    article_tag: str  # HTML-тег для статей
    article_selectors: List[str]  # Список CSS-селекторов для статей


class SiteMapExtractor:
    """
    Класс для извлечения карты сайта.
    """
    def __init__(self, options: ExtractorOptions):
        """
        Инициализация экстрактора с заданными настройками.
        """
        self.options = options

    def extract_categories_recursive(self, url=None, parent: Category = None, visited=None) -> List[Category]:
        """
        Рекурсивно извлекает категории и подкатегории с указанного URL.
        """
        if url is None:
            url = self.options.root_url  # Используем корневой URL, если текущий не указан

        excluded_urls = self.options.excluded_urls  # Ссылки, которые нужно игнорировать
        category_tag = self.options.category_tag
        category_selectors = self.options.category_selectors

        # Выполняем запрос к странице
        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')  # Парсим HTML-страницу
        categories: list[Category] = []  # Список категорий

        # Перебираем все заданные селекторы для категорий
        for selector in category_selectors:
            compiled_selector = f"{category_tag}.{selector}"
            for category in soup.select(compiled_selector):
                sub_url = urljoin(url, category['href'])  # Преобразуем относительные пути в абсолютные

                if sub_url in excluded_urls:
                    continue  # Пропускаем ссылки из списка исключений

                name = category.text.strip()  # Извлекаем текст категории
                articles = self.extract_articles(soup, sub_url)  # Извлекаем статьи для категории

                # Создаём объект категории
                parsed_category = Category(name=name, url=sub_url, subcategories=[], articles=[])

                # Рекурсивно извлекаем подкатегории
                subcategories = self.extract_categories_recursive(url=sub_url, parent=parsed_category, visited=visited)
                parsed_category.subcategories = subcategories

                # Проверяем, добавлена ли уже такая категория
                if not any(cat.url == sub_url for cat in categories):
                    categories.append(parsed_category)

        if not categories:  # Если категорий не найдено, извлекаем статьи
            articles = self.extract_articles(soup, url)
            if articles and parent:
                parent.articles.extend(articles)  # Добавляем статьи в родительскую категорию
        return categories

    def extract_articles(self, soup: BeautifulSoup, url: str) -> List[Article]:
        """
        Извлекает статьи с указанного URL.
        """
        article_tag = self.options.article_tag
        article_selectors = self.options.article_selectors

        articles = []
        # Перебираем все заданные селекторы для статей
        for selector in article_selectors:
            compiled_selector = f"{article_tag}.{selector}"
            for article in soup.select(compiled_selector):
                article_url = urljoin(url, article['href'])  # Преобразуем относительный путь в абсолютный

                if article_url in self.options.excluded_urls:
                    continue  # Пропускаем ссылки из списка исключений

                # Извлекаем заголовок статьи
                article_title = article.select_one('.title').text.strip().replace('\n', ' ').replace('\r', '') \
                    if article.select_one('.title') else "Untitled"

                articles.append(Article(title=article_title, url=article_url))
        return articles

    def extract_site_map(self) -> SiteMap:
        """
        Создаёт и возвращает объект SiteMap.
        """
        categories = self.extract_categories_recursive()  # Извлекаем все категории
        return SiteMap(root_url=self.options.root_url, categories=categories)

    def extract_and_export_results(self, filename: str):
        """
        Извлекает карту сайта и экспортирует её в файл.
        """
        site_map = self.extract_site_map()
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(site_map, file, indent=4, ensure_ascii=False, default=lambda o: o.__dict__)

    def export_results(self, site_map: SiteMap, filename: str):
        """
        Экспортирует объект SiteMap в файл.
        """
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(site_map, file, indent=4, ensure_ascii=False, default=lambda o: o.__dict__)

    def load_site_map_from_json(self, filename: str) -> SiteMap:
        """
        Загружает карту сайта из JSON-файла и восстанавливает объект SiteMap.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return self._dict_to_sitemap(data)

    def _dict_to_sitemap(self, data: dict) -> SiteMap:
        """
        Преобразует словарь в объект SiteMap.
        """
        root_url = data['root_url']
        categories = [self._dict_to_category(category) for category in data['categories']]
        return SiteMap(root_url=root_url, categories=categories)

    def _dict_to_category(self, data: dict) -> Category:
        """
        Преобразует словарь в объект Category.
        """
        name = data['name']
        url = data['url']
        subcategories = [self._dict_to_category(subcategory) for subcategory in data.get('subcategories', [])]
        articles = [self._dict_to_article(article) for article in data.get('articles', [])]
        return Category(name=name, url=url, subcategories=subcategories, articles=articles)

    def _dict_to_article(self, data: dict) -> Article:
        """
        Преобразует словарь в объект Article.
        """
        title = data['title']
        url = data['url']
        return Article(title=title, url=url)

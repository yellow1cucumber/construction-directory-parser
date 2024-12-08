import json
from urllib.parse import urljoin
from typing import List

import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel

from core.sitemap_extraction.category import Category
from core.sitemap_extraction.article import Article
from core.sitemap_extraction.sitemap import SiteMap


class ExtractorOptions(BaseModel):
    """
    A model to store parser settings.

    Attributes:
        root_url (str): The root URL to start parsing from.
        excluded_urls (list[str]): A list of URLs to exclude from parsing.
        category_tag (str): The HTML tag used to identify categories.
        category_selectors (List[str]): CSS selectors used to locate categories.
        article_tag (str): The HTML tag used to identify articles.
        article_selectors (List[str]): CSS selectors used to locate articles.
    """
    root_url: str
    excluded_urls: list[str]
    category_tag: str
    category_selectors: List[str]
    article_tag: str
    article_selectors: List[str]


class SiteMapExtractor:
    """
    A class to extract a website's sitemap structure.

    Methods:
        __init__(options: ExtractorOptions):
            Initializes the extractor with the specified options.

        extract_categories_recursive(url=None, parent=None, visited=None) -> List[Category]:
            Recursively extracts categories and subcategories from the given URL.

        extract_articles(soup: BeautifulSoup, url: str) -> List[Article]:
            Extracts articles from the provided URL.

        extract_site_map() -> SiteMap:
            Creates and returns a `SiteMap` object.

        extract_and_export_results(filename: str):
            Extracts the sitemap and exports it to a file.

        export_results(site_map: SiteMap, filename: str):
            Exports a `SiteMap` object to a file.

        load_site_map_from_json(filename: str) -> SiteMap:
            Loads a sitemap from a JSON file and returns a `SiteMap` object.

        _dict_to_sitemap(data: dict) -> SiteMap:
            Converts a dictionary to a `SiteMap` object.

        _dict_to_category(data: dict) -> Category:
            Converts a dictionary to a `Category` object.

        _dict_to_article(data: dict) -> Article:
            Converts a dictionary to an `Article` object.
    """
    def __init__(self, options: ExtractorOptions):
        """
        Initializes the extractor with the specified options.

        Args:
            options (ExtractorOptions): The options for parsing.
        """
        self.options = options

    def extract_categories_recursive(self, url=None, parent: Category = None, visited=None) -> List[Category]:
        """
        Recursively extracts categories and subcategories from the given URL.

        Args:
            url (str, optional): The URL to start extraction. Defaults to the root URL.
            parent (Category, optional): The parent category for nesting subcategories.
            visited (set, optional): A set of visited URLs to avoid cycles.

        Returns:
            List[Category]: A list of extracted categories.
        """
        if url is None:
            url = self.options.root_url

        response = requests.get(url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        categories: list[Category] = []

        for selector in self.options.category_selectors:
            compiled_selector = f"{self.options.category_tag}.{selector}"
            for category in soup.select(compiled_selector):
                sub_url = urljoin(url, category['href'])

                if sub_url in self.options.excluded_urls:
                    continue

                name = category.text.strip()
                articles = self.extract_articles(soup, sub_url)
                parsed_category = Category(name=name, url=sub_url, subcategories=[], articles=articles)

                subcategories = self.extract_categories_recursive(url=sub_url, parent=parsed_category, visited=visited)
                parsed_category.subcategories = subcategories

                if not any(cat.url == sub_url for cat in categories):
                    categories.append(parsed_category)

        if not categories and parent:
            articles = self.extract_articles(soup, url)
            parent.articles.extend(articles)

        return categories

    def extract_articles(self, soup: BeautifulSoup, url: str) -> List[Article]:
        """
        Extracts articles from the provided URL.

        Args:
            soup (BeautifulSoup): The parsed HTML content of the page.
            url (str): The URL of the page being parsed.

        Returns:
            List[Article]: A list of extracted articles.
        """
        articles = []
        for selector in self.options.article_selectors:
            compiled_selector = f"{self.options.article_tag}.{selector}"
            for article in soup.select(compiled_selector):
                article_url = urljoin(url, article['href'])

                if article_url in self.options.excluded_urls:
                    continue

                article_title = (
                    article.select_one('.title').text.strip()
                    if article.select_one('.title') else "Untitled"
                )
                articles.append(Article(title=article_title, url=article_url))
        return articles

    def extract_site_map(self) -> SiteMap:
        """
        Creates and returns a `SiteMap` object.

        Returns:
            SiteMap: The extracted sitemap.
        """
        categories = self.extract_categories_recursive()
        return SiteMap(root_url=self.options.root_url, categories=categories)

    def extract_and_export_results(self, filename: str):
        """
        Extracts the sitemap and exports it to a file.

        Args:
            filename (str): The path to the file where the sitemap will be saved.
        """
        site_map = self.extract_site_map()
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(site_map, file, indent=4, ensure_ascii=False, default=lambda o: o.__dict__)

    def export_results(self, site_map: SiteMap, filename: str):
        """
        Exports a `SiteMap` object to a file.

        Args:
            site_map (SiteMap): The sitemap to export.
            filename (str): The path to the file where the sitemap will be saved.
        """
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(site_map, file, indent=4, ensure_ascii=False, default=lambda o: o.__dict__)

    def load_site_map_from_json(self, filename: str) -> SiteMap:
        """
        Loads a sitemap from a JSON file.

        Args:
            filename (str): The path to the JSON file containing the sitemap.

        Returns:
            SiteMap: The loaded sitemap object.
        """
        with open(filename, 'r', encoding='utf-8') as file:
            data = json.load(file)

        return self._dict_to_sitemap(data)

    def _dict_to_sitemap(self, data: dict) -> SiteMap:
        """
        Converts a dictionary to a `SiteMap` object.

        Args:
            data (dict): The dictionary representation of a sitemap.

        Returns:
            SiteMap: The reconstructed `SiteMap` object.
        """
        root_url = data['root_url']
        categories = [self._dict_to_category(category) for category in data['categories']]
        return SiteMap(root_url=root_url, categories=categories)

    def _dict_to_category(self, data: dict) -> Category:
        """
        Converts a dictionary to a `Category` object.

        Args:
            data (dict): The dictionary representation of a category.

        Returns:
            Category: The reconstructed `Category` object.
        """
        name = data['name']
        url = data['url']
        subcategories = [self._dict_to_category(subcategory) for subcategory in data.get('subcategories', [])]
        articles = [self._dict_to_article(article) for article in data.get('articles', [])]
        return Category(name=name, url=url, subcategories=subcategories, articles=articles)

    def _dict_to_article(self, data: dict) -> Article:
        """
        Converts a dictionary to an `Article` object.

        Args:
            data (dict): The dictionary representation of an article.

        Returns:
            Article: The reconstructed `Article` object.
        """
        title = data['title']
        url = data['url']
        return Article(title=title, url=url)

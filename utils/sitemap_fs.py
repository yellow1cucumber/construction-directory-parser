import os
import json
import base64

from core.sitemap_extraction.article import Article
from core.sitemap_extraction.category import Category
from core.sitemap_extraction.sitemap import SiteMap

def serialize_bytes(data):
    """
    Рекурсивно преобразует поля типа bytes в строку Base64 в словаре или списке.
    """
    if isinstance(data, dict):
        return {k: serialize_bytes(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [serialize_bytes(item) for item in data]
    elif isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')  # Конвертируем в строку Base64
    return data

def save_article_to_json(article: Article, directory: str):
    """
    Сохраняет статью в формате JSON в указанной директории.

    Args:
        article (Article): Объект статьи для сохранения.
        directory (str): Путь к директории, где сохранить файл.
    """
    os.makedirs(directory, exist_ok=True)
    file_path = os.path.join(directory, f"{article.title}.json")
    article_data = serialize_bytes(article.dict())  # Преобразуем bytes в строку
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(article_data, file, ensure_ascii=False, indent=4)


def save_category_to_filesystem(category: Category, parent_directory: str):
    """
    Рекурсивно сохраняет категории и статьи из объекта Category в файловой системе.

    Args:
        category (Category): Объект категории для сохранения.
        parent_directory (str): Родительская директория для текущей категории.
    """
    # Создать директорию для текущей категории
    category_directory = os.path.join(parent_directory, category.name)
    os.makedirs(category_directory, exist_ok=True)

    # Сохранить статьи категории
    for article in category.articles:
        save_article_to_json(article, category_directory)

    # Рекурсивно сохранить подкатегории
    for subcategory in category.subcategories:
        save_category_to_filesystem(subcategory, category_directory)


def save_sitemap_to_filesystem(sitemap: SiteMap, root_directory: str):
    """
    Сохраняет объект SiteMap в файловую систему.

    Args:
        sitemap (SiteMap): Объект SiteMap для сохранения.
        root_directory (str): Корневая директория для сохранения данных.
    """
    os.makedirs(root_directory, exist_ok=True)

    for category in sitemap.categories:
        save_category_to_filesystem(category, root_directory)

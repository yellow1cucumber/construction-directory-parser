import os
import re

import shutil
import json
import hashlib

from transliterate import translit

from core.content_parsing.image_parser import HTMLImageParser
from core.sitemap_extraction.sitemap import SiteMap
from core.sitemap_extraction.article import Article
from core.sitemap_extraction.category import Category


class SiteMapFS:
    """
    A class to save a sitemap and its articles' images to the file system with safe, hashed paths.
    """
    def __init__(self, base_dir: str):
        self.base_dir = base_dir

    def __hash_path_name(self, name: str) -> str:
        """
        Generates a short and unique hash for a given name.

        Args:
            name (str): The original name to hash.

        Returns:
            str: A hashed name safe for use in file paths.
        """
        hash_digest = hashlib.md5(name.encode('utf-8')).hexdigest()[:16]  # Use the first 16 chars for brevity
        return hash_digest

    def save_article(self, article: Article, article_dir: str):
        """
        Saves an article's HTML and associated images to a hashed directory.

        Args:
            article (Article): The article object to save.
            article_dir (str): The directory where the article should be saved.
        """
        hashed_article_dir = os.path.join(article_dir, self.__hash_path_name(article.title))
        os.makedirs(hashed_article_dir, exist_ok=True)
        image_dir = os.path.join(hashed_article_dir, 'images')

        # Update image links and save HTML
        updated_html = HTMLImageParser.update_image_links(article, image_dir)
        article_path = os.path.join(hashed_article_dir, f"{self.__hash_path_name(article.title)}")
        with open(article_path, 'w', encoding='utf-8') as file:
            file.write(updated_html)
        print(f"Saved article with updated links: {article_path}")

    def save_category(self, category: Category, parent_dir: str):
        """
        Saves a category and its contents to hashed directories.

        Args:
            category (Category): The category object to save.
            parent_dir (str): The parent directory where the category should be saved.
        """
        hashed_category_dir = os.path.join(parent_dir, self.__hash_path_name(category.name))
        os.makedirs(hashed_category_dir, exist_ok=True)
        print(f"Processing category: {hashed_category_dir}")

        for article in category.articles:
            self.save_article(article, hashed_category_dir)

        subcategories = []
        for subcategory in category.subcategories:
            subcategories.append(self.save_category(subcategory, hashed_category_dir))

        return {
            "name": category.name,
            "path": hashed_category_dir,
            "subcategories": subcategories,
            "articles": [
                {
                    "title": article.title,
                    "path": os.path.join(hashed_category_dir, f"{self.__hash_path_name(article.title)}", f"{self.__hash_path_name(article.title)}")
                } for article in category.articles
            ]
        }

    def save_sitemap(self, sitemap: SiteMap):
        """
        Saves the sitemap structure with hashed paths to ensure compatibility.

        Args:
            sitemap (SiteMap): The sitemap object to save.
        """
        print("Saving sitemap...")
        hashed_root_dir = os.path.join(self.base_dir, self.__hash_path_name(sitemap.root_url))
        os.makedirs(hashed_root_dir, exist_ok=True)

        sitemap_structure = []
        for category in sitemap.categories:
            sitemap_structure.append(self.save_category(category, hashed_root_dir))

        # Save sitemap index
        index_path = os.path.join(hashed_root_dir, 'sitemap_index.json')
        with open(index_path, 'w', encoding='utf-8') as index_file:
            json.dump(sitemap_structure, index_file, indent=4, ensure_ascii=False)
        print(f"Sitemap index saved at: {index_path}")

    def save_as_zip(self, sitemap: SiteMap, zip_filename: str):
        """
        Saves the entire sitemap directory as a zip archive.

        Args:
            sitemap (SiteMap): The sitemap object.
            zip_filename (str): The path and name of the zip file to create.
        """
        hashed_root_dir = os.path.join(self.base_dir, self.__hash_path_name(sitemap.root_url))
        zip_path = os.path.abspath(zip_filename)
        print(f"Creating zip archive: {zip_path}")
        try:
            shutil.make_archive(zip_path.replace('.zip', ''), 'zip', hashed_root_dir)
            print(f"Successfully created zip archive at: {zip_path}")
        except Exception as e:
            print(f"Error creating zip archive: {e}")

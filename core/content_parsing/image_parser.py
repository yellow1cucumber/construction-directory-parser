import os
import requests
import hashlib

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from core.sitemap_extraction.article import Article


class HTMLImageParser:
    """
    A class to parse HTML, extract image URLs, download them, and save locally with minimal file names.
    """
    @staticmethod
    def extract_images(article: Article) -> list[str]:
        """
        Extracts all image URLs from the article's HTML content.

        Args:
            article (Article): The article containing HTML content and URL.

        Returns:
            list[str]: A list of full image URLs.
        """
        soup = BeautifulSoup(article.html, 'html.parser')
        image_tags = soup.find_all('img')
        image_urls = [urljoin(article.url, img.get('src')) for img in image_tags if img.get('src')]
        return image_urls

    @staticmethod
    def download_image(url: str, save_dir: str, index: int = None) -> str:
        """
        Downloads an image from a URL, saves it locally with a short and safe file name.

        Args:
            url (str): The image URL to download.
            save_dir (str): Directory to save the downloaded image.
            index (int, optional): Optional index for unique naming.

        Returns:
            str: The local path of the saved image or an empty string if download fails.
        """
        os.makedirs(save_dir, exist_ok=True)

        # Generate a short unique name for the file
        hash_digest = hashlib.md5(url.encode('utf-8')).hexdigest()[:8]
        filename = f"img_{index}_{hash_digest}.jpg" if index is not None else f"img_{hash_digest}.jpg"
        local_path = os.path.join(save_dir, filename)

        try:
            response = requests.get(url, stream=True, timeout=10)
            response.raise_for_status()
            with open(local_path, 'wb') as img_file:
                for chunk in response.iter_content(1024):
                    img_file.write(chunk)
            print(f"Downloaded: {url} -> {local_path}")
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            return ""
        return local_path

    @classmethod
    def save_images(cls, article: Article, save_dir: str) -> dict[str, str]:
        """
        Downloads and saves images from the article, mapping original URLs to local paths.

        Args:
            article (Article): The article object containing HTML content and URL.
            save_dir (str): Directory to save images.

        Returns:
            dict[str, str]: Mapping of original image URLs to local paths.
        """
        image_urls = cls.extract_images(article)
        local_paths = {}
        for index, img_url in enumerate(image_urls):
            local_path = cls.download_image(img_url, save_dir, index)
            if local_path:
                local_paths[img_url] = os.path.relpath(local_path, save_dir)
        return local_paths

    @classmethod
    def update_image_links(cls, article: Article, save_dir: str) -> str:
        """
        Updates the `src` attributes of all image tags in the article's HTML,
        replacing them with local paths to the downloaded images.

        Args:
            article (Article): The article containing the HTML content.
            save_dir (str): Directory to save the images.

        Returns:
            str: The updated HTML content.
        """
        # Parse the HTML
        soup = BeautifulSoup(article.html, 'html.parser')

        # Download images and get their mappings
        image_mappings = cls.save_images(article, save_dir)

        # Update the `src` attributes in the HTML
        for img_tag in soup.find_all('img'):
            img_url = urljoin(article.url, img_tag.get('src', ''))
            if img_url in image_mappings:
                img_tag['src'] = os.path.join('images', image_mappings[img_url])

        # Return the updated HTML as a string
        return str(soup)

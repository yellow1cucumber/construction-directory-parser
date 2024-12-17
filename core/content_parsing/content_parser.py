import re
import requests
from typing import List

from bs4 import BeautifulSoup, Tag

from core.content_parsing.contentElement import ContentElement
from core.content_parsing.pageContent import PageContent


class ContentParser:
    """
    A class for parsing and extracting structured content from a web page.

    Attributes:
        url (str): The URL of the web page to parse.
        html_content (str): The raw HTML content of the web page.
        soup (BeautifulSoup): The parsed HTML content.
        container_selector (str): The CSS selector for the main content container.
        content_elements (List[ContentElement]): A list of extracted content elements.
        subheading_pattern (Pattern): A regex pattern to identify subheadings.
    """

    def __init__(self, url: str, container_selector: str):
        """
        Initializes the ContentParser with a URL and container selector.

        Args:
            url (str): The URL of the page to parse.
            container_selector (str): The CSS selector for the content container.
        """
        self.url = url
        self.html_content = ''
        self.soup: BeautifulSoup | None = None
        self.container_selector = container_selector
        self.content_elements: List[ContentElement] = []
        self.subheading_pattern = re.compile(r'^\s*\d+(\.\d+)*\.\s+.+')

    def fetch_content(self):
        """
        Fetches the raw HTML content from the URL.

        Raises:
            HTTPError: If the HTTP request fails.
        """
        response = requests.get(self.url)
        response.raise_for_status()
        self.html_content = response.text

    def parse_html(self):
        """
        Parses the fetched HTML content using BeautifulSoup.
        """
        self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def parse_and_get_pure_html(self) -> str:
        """
        Parse and return pure html from container
        """
        if not self.soup:
            self.fetch_content()
            self.parse_html()

        return self.soup.prettify()

    def get_text_content(self, element):
        """
        Extracts text content from an HTML element.

        Args:
            element (Tag): The HTML element to extract text from.

        Returns:
            str: The stripped text content of the element.
        """
        return ' '.join(element.stripped_strings).strip()

    def is_subheading(self, text):
        """
        Determines if a given text matches the subheading pattern.

        Args:
            text (str): The text to evaluate.

        Returns:
            bool: True if the text matches the subheading pattern, False otherwise.
        """
        return bool(self.subheading_pattern.match(text))

    def process_table_of_contents(self, table: Tag):
        """
        Processes a table element, extracting links or adding it as raw HTML.

        Args:
            table (Tag): The table element to process.
        """
        if table.select_one('a'):
            for link in table.find_all('a'):
                href = link.get('href', '')
                text = self.get_text_content(link)
                if href and text:
                    self.content_elements.append(ContentElement(
                        type='link',
                        content=href,
                        attributes={
                            'text': text,
                            'title': link.get('title', ''),
                            'target': link.get('target', '')
                        }
                    ))
        else:
            self.content_elements.append(ContentElement(
                type='table',
                content='',
                attributes={'html': table.prettify()}
            ))

    def process_heading(self, text):
        """
        Processes text as either a subheading or a paragraph.

        Args:
            text (str): The text to process.
        """
        content_type = 'subheading' if self.is_subheading(text) else 'paragraph'
        self.content_elements.append(ContentElement(
            type=content_type,
            content=text,
            attributes={}
        ))

    def get_markup(self) -> str:
        container = self.soup.select_one(self.container_selector)
        if not container:
            raise ValueError(f"Container with selector '{self.container_selector}' not found.")

        return container.prettify()


    def parse_container(self):
        """
        Parses the main content container and extracts elements.

        Raises:
            ValueError: If the container cannot be found using the selector.
        """
        container = self.soup.select_one(self.container_selector)
        if not container:
            raise ValueError(f"Container with selector '{self.container_selector}' not found.")

        for element in container.find_all(recursive=False):
            if element.name == 'table':
                self.process_table_of_contents(element)
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                text = self.get_text_content(element)
                if text:
                    self.content_elements.append(ContentElement(
                        type='heading',
                        content=text,
                        attributes={'level': element.name}
                    ))
            elif element.name == 'p':
                text = self.get_text_content(element)
                if text:
                    self.process_heading(text)
            elif element.name == 'img':
                src = element.get('src', '')
                if src:
                    self.content_elements.append(ContentElement(
                        type='image',
                        content=src,
                        attributes={
                            'alt': element.get('alt', ''),
                            'title': element.get('title', ''),
                            'width': element.get('width', ''),
                            'height': element.get('height', '')
                        }
                    ))

    def parse(self, only_markup: bool = False) -> str | PageContent:
        """
        Main method to fetch, parse, and extract content elements.

        Returns:
            PageContent: The parsed content as a structured `PageContent` object.
        """
        self.fetch_content()
        self.parse_html()

        if only_markup:
            markup = self.get_markup()
            return markup

        self.parse_container()
        return PageContent(elements=self.content_elements)

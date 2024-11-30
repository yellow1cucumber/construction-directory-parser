import os
import re
import requests
from bs4 import BeautifulSoup
from typing import List

from pydantic import BaseModel

from core.parsing.contentElement import ContentElement
from core.parsing.pageContent import PageContent


# Define the ContentParser class
class ContentParser:
    def __init__(self, url: str, container_selector: str):
        self.url = url
        self.html_content = ''
        self.soup = None
        self.container_selector = container_selector
        self.content_elements: List[ContentElement] = []
        # Regular expression for subheadings
        self.subheading_pattern = re.compile(r'^\s*\d+(\.\d+)*\.\s+.+')

    def fetch_content(self):
        """Fetches HTML content from the URL."""
        response = requests.get(self.url)
        response.raise_for_status()
        self.html_content = response.text

    def parse_html(self):
        """Parses the HTML content using BeautifulSoup."""
        self.soup = BeautifulSoup(self.html_content, 'html.parser')

    def get_text_content(self, element):
        """Extracts text content from an HTML element."""
        return ' '.join(element.stripped_strings).strip()

    def is_subheading(self, text):
        """Checks if a given text matches the subheading pattern."""
        return bool(self.subheading_pattern.match(text))

    def process_table_of_contents(self, table):
        """Processes the table of contents, extracting images and links."""
        # Process images in the table
        for img in table.find_all('img'):
            src = img.get('src', '')
            if src:
                self.content_elements.append(ContentElement(
                    type='image',
                    content=src,
                    attributes={
                        'alt': img.get('alt', ''),
                        'title': img.get('title', ''),
                        'width': img.get('width', ''),
                        'height': img.get('height', '')
                    }
                ))
        # Process links in the table
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

    def process_heading(self, text):
        """Processes text to determine if it's a subheading or a paragraph."""
        if self.is_subheading(text):
            content_type = 'subheading'
        else:
            content_type = 'paragraph'
        self.content_elements.append(ContentElement(
            type=content_type,
            content=text,
            attributes={}
        ))

    def parse_container(self):
        """Parses the main content container and extracts elements."""
        container = self.soup.select_one(self.container_selector)
        if not container:
            raise ValueError(f"Container with selector '{self.container_selector}' not found.")

        # Iterate over the immediate children of the container
        for element in container.find_all(recursive=False):
            if element.name == 'table':
                # Process table of contents
                self.process_table_of_contents(element)
            elif element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # Process headings
                text = self.get_text_content(element)
                if text:
                    self.content_elements.append(ContentElement(
                        type='heading',
                        content=text,
                        attributes={'level': element.name}
                    ))
            elif element.name == 'p':
                # Process paragraphs and subheadings
                text = self.get_text_content(element)
                if text:
                    self.process_heading(text)
            elif element.name == 'img':
                # Process images outside tables
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
            else:
                # Process other elements if necessary
                pass

    def parse(self):
        """Main method to fetch, parse, and extract content elements."""
        self.fetch_content()
        self.parse_html()
        self.parse_container()
        # Create PageContent instance
        page_content = PageContent(elements=self.content_elements)
        return page_content
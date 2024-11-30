import os
import re
from typing import List, Union

from bs4 import BeautifulSoup
from pydantic import BaseModel

from core.parsing.contentElement import ContentElement
from core.parsing.pageContent import PageContent


class ContentParser:
    SUBTITLE_STYLES = ['font-size: x-large', 'color: #3366ff']
    SUBTITLE_REGEX = re.compile(r'^\d+\.\s')

    def parse_content(self, html: str, container_class: str) -> PageContent:
        """Парсит HTML и возвращает структуру PageContent."""
        soup = BeautifulSoup(html, 'html.parser')
        page_content = PageContent(elements=[])

        container = soup.find(class_=container_class)
        if not container:
            return page_content

        for tag in container.find_all(['h1', 'p', 'img', 'table', 'a', 'iframe']):
            parsed_element = self.parse_tag(tag)
            if parsed_element:
                if isinstance(parsed_element, list):  # Для таблиц, возвращающих список
                    page_content.elements.extend(parsed_element)
                else:
                    page_content.elements.append(parsed_element)
        return page_content

    def parse_tag(self, tag) -> Union[ContentElement, List[ContentElement], None]:
        """Обрабатывает отдельный HTML-тег и возвращает ContentElement."""
        if tag.name == 'h1':
            return ContentElement(type='heading', content=tag.text.strip())

        elif tag.name == 'p':
            return ContentElement(
                type='subtitle' if self.is_subtitle(tag) else 'paragraph',
                content=tag.text.strip()
            )

        elif tag.name == 'img':
            return ContentElement(type='image', content='', attributes={'src': tag.get('src')})

        elif tag.name == 'a':
            return ContentElement(
                type='link',
                content=tag.text.strip(),
                attributes={'href': tag.get('href')}
            )

        elif tag.name == 'table':
            # Проверяем, есть ли в таблице ссылки
            if tag.find_all('a', href=True):  # Если есть ссылки, используем parse_link_table
                return self.parse_link_table(tag)
            else:  # Иначе используем parse_table
                return self.parse_tablie(tag)

        elif tag.name == 'iframe':
            return ContentElement(
                type='doc-view',
                content=tag.text.strip(),
                attributes={
                    'src': tag.get('src')
                })
        return None  # Возвращаем None для неизвестных тегов

    def is_subtitle(self, tag) -> bool:
        """Проверяет, является ли тег подзаголовком."""
        styles = tag.get('style', '')
        if any(style in styles for style in self.SUBTITLE_STYLES):
            return True

        strong_tag = tag.find('strong')
        if strong_tag and self.SUBTITLE_REGEX.match(strong_tag.text.strip()):
            return True

        if self.SUBTITLE_REGEX.match(tag.get_text(strip=True)):
            return True

        return False

    def parse_link_table(self, tag) -> List[ContentElement]:
        """Обрабатывает таблицу и возвращает список ссылок."""
        return [
            ContentElement(type='link-table', content=link.text.strip(), attributes={'href': link.get('href')})
            for link in tag.find_all('a', href=True)
        ]

    def parse_tablie(self, tag) -> List[ContentElement]:
        rows = tag.find_all("tr")  # Извлекаем строки таблицы
        if not rows:
            return []

        headers = []
        data = []

        for i, row in enumerate(rows):
            cells = row.find_all(["td", "th"])
            cell_text = [cell.get_text(strip=True) for cell in cells]

            if i == 0:  # Первая строка - заголовки
                headers = cell_text
            else:  # Остальные строки - данные
                row_dict = dict(zip(headers, cell_text))
                data.append(ContentElement(type='table', content='', attributes=row_dict))
        return data


    def save_to_json(self, data: BaseModel, file_path: str) -> None:
        """Сохраняет данные в JSON-файл."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(data.model_dump_json())
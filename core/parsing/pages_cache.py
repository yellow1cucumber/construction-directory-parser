from pathlib import Path

from pydantic import BaseModel, Field

from core.extraction.article import Article


class PagesCache(BaseModel):
    cache: list[tuple[Article, str]] = Field(default_factory=list)

    def save(self, page: Article, path: str):
        # Сохраняем путь как строку в POSIX-формате
        path_str = Path(path).as_posix()
        for i, (existing_page, _) in enumerate(self.cache):
            if existing_page == page:
                self.cache[i] = (page, path_str)
                return
        self.cache.append((page, path_str))

    def get(self, page: Article) -> Path | None:
        for existing_page, path_str in self.cache:
            if existing_page == page:
                return Path(path_str)
        return None

    def get_by_url(self, url: str) -> Path | None:
        for existing_page, path_str in self.cache:
            if existing_page.url == url:
                return Path(path_str)
        return None

    def get_by_id(self, page_id: int) -> Path | None:
        for existing_page, path_str in self.cache:
            if existing_page.url.endswith(str(page_id)):
                return Path(path_str)
        return None

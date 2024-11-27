from pydantic import BaseModel, Field

from core.extraction.article import Article


class PagesCache(BaseModel):
    cache: list[tuple[Article, str]] = Field(default_factory=list)

    def save(self, page: Article, path: str):
        for i, (existing_page, _) in enumerate(self.cache):
            if existing_page == page:
                self.cache[i] = (page, path)
                return
        self.cache.append((page, path))

    def get(self, page: Article) -> str | None:
        for existing_page, path in self.cache:
            if existing_page == page:
                return path
        return None

    def get_by_url(self, url: str) -> str | None:
        for existing_page, path in self.cache:
            if existing_page.url == url:
                return path
        return None

    def get_by_id(self, page_id: int) -> str | None:
        for existing_page, path in self.cache:
            if existing_page.url.endswith(str(page_id)):
                return path
        return None

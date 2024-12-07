from pydantic import BaseModel, Field

from core.extraction.sitemap import SiteMap
from core.extraction.sitemapExtractor import ExtractorOptions


class ServerState(BaseModel):
    extractor_options: ExtractorOptions | None = None
    extraction_file: str | None = None
    sitemap: SiteMap | None = None
    default_sitemap_export_file: str = 'extraction.json'

    pages_content_container_selector: str = 'page_text'

    default_parsed_data_dir: str = 'data'
    parsed_data_dir: str | None = default_parsed_data_dir

    def update(self, new_data: dict):
        """
        Update the state with new data.

        :param new_data: Dictionary of new state values.
        """
        for key, value in new_data.items():
            if key in self.__fields__:
                setattr(self, key, value)
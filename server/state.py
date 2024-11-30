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
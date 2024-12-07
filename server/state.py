from pydantic import BaseModel

from reactivex import Observable
from reactivex.subject import BehaviorSubject

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


class ServerStateProvider:
    _server_state: BehaviorSubject[ServerState]

    def __init__(self, init_state: ServerState = ServerState()):
        self._server_state = BehaviorSubject(init_state)

    def as_observable(self) -> Observable[ServerState]:
        return self._server_state

    def update_state(self, new_state: ServerState):
        self._server_state.on_next(new_state)

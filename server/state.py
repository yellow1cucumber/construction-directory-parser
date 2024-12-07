from pydantic import BaseModel
from reactivex import Observable
from reactivex.subject import BehaviorSubject
from core.extraction.sitemap import SiteMap
from core.extraction.sitemapExtractor import ExtractorOptions


class ServerState(BaseModel):
    """
    Represents the state of the server, including configuration, sitemap, and data directories.

    Attributes:
        extractor_options (ExtractorOptions | None): Options for the sitemap extractor.
        extraction_file (str | None): Path to the file containing extraction data.
        sitemap (SiteMap | None): The current sitemap loaded in the server state.
        default_sitemap_export_file (str): Default filename for exporting the sitemap. Defaults to 'extraction.json'.
        pages_content_container_selector (str): CSS selector for the main content container on pages.
        default_parsed_data_dir (str): Default directory for storing parsed data. Defaults to 'data'.
        parsed_data_dir (str | None): Directory for storing parsed data, defaults to `default_parsed_data_dir`.
    """
    extractor_options: ExtractorOptions | None = None
    extraction_file: str | None = None
    sitemap: SiteMap | None = None
    default_sitemap_export_file: str = 'extraction.json'
    pages_content_container_selector: str = 'page_text'
    default_parsed_data_dir: str = 'data'
    parsed_data_dir: str | None = default_parsed_data_dir


class ServerStateProvider:
    """
    Manages the state of the server using a reactive pattern.

    Attributes:
        _server_state (BehaviorSubject[ServerState]): Reactive subject holding the current server state.

    Methods:
        as_observable() -> Observable[ServerState]:
            Returns the current server state as an observable for reactive updates.

        update_state(new_state: ServerState):
            Updates the server state and notifies all observers.
    """

    _server_state: BehaviorSubject[ServerState]

    def __init__(self, init_state: ServerState = ServerState()):
        """
        Initializes the server state provider with an initial state.

        Args:
            init_state (ServerState): The initial state of the server. Defaults to a new `ServerState` instance.
        """
        self._server_state = BehaviorSubject(init_state)

    def as_observable(self) -> Observable[ServerState]:
        """
        Returns the current server state as an observable.

        This allows observers to subscribe and react to state updates.

        Returns:
            Observable[ServerState]: An observable stream of the server state.
        """
        return self._server_state

    def update_state(self, new_state: ServerState):
        """
        Updates the server state and notifies all observers.

        Args:
            new_state (ServerState): The new state to apply.
        """
        self._server_state.on_next(new_state)

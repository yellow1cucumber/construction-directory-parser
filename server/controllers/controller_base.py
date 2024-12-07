from abc import ABC, abstractmethod

from flask import Flask

from server.state import ServerState, ServerStateProvider

class BaseController(ABC):
    _app: Flask
    _state_provider: ServerStateProvider
    _state: ServerState

    def __init__(self, app: Flask, state_provider: ServerStateProvider):
        self._app = app
        self._state_provider = state_provider
        self._state_provider.as_observable().subscribe(
            on_next=self.on_state_update,
            on_error=self.on_error
        )

    @abstractmethod
    def init_endpoints(self):
        raise NotImplemented()

    def on_state_update(self, new_state: ServerState) -> None:
        try:
            self._state = new_state
        except Exception as e:
            print(str(e))

    def on_error(self, error: Exception):
        raise Exception(f"Error in {self.__class__.__name__}: {error}")
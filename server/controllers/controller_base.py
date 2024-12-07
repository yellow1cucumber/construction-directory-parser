from abc import ABC, abstractmethod

from flask import Flask

from server.state import ServerState

class BaseController(ABC):
    _app: Flask
    state: ServerState

    def __init__(self, app: Flask, state: ServerState):
        self._app = app
        self.state = state

    @abstractmethod
    def init_endpoints(self):
        raise NotImplemented()
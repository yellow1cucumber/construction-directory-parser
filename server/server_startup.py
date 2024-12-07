from typing import List, Type

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from pydantic import BaseModel

from server.controllers.controller_base import BaseController
from server.init_state import InitConfiguration
from server.state import ServerState


class RunSettings(BaseModel):
    host: str
    port: int
    debug: bool

    @staticmethod
    def get_default_dev():
        return RunSettings(
            host="0.0.0.0",
            port=5000,
            debug=True,
        )

    @staticmethod
    def get_default_prod():
        return RunSettings(
            host="0.0.0.0",
            port=5000,
            debug=False,
        )


class Startup:
    app: Flask
    state: ServerState
    controllers: List[BaseController] = []

    def init_server(self, name: str = "") -> None:
        """
        Initializes the Flask application.
        """
        self.app = Flask(name)

    def init_state(self) -> None:
        """
        Initializes the server state by loading it from a configuration file if available.
        """
        config_path = InitConfiguration.find_config_path()
        if config_path:
            self.state = InitConfiguration.serialize_from_file(config_path)
            return
        self.state = ServerState()

    def init_cors_dev(self, origins: List[str] = ["*"]) -> None:
        """
        Initializes CORS for the development environment.

        :param origins: List of allowed origins. Defaults to all origins.
        """
        CORS(self.app, resources={r"/*": {"origins": origins}})

    def add_controller(self, controller_type: Type[BaseController]) -> None:
        """
        Adds a controller to the application.

        :param controller_type: The controller class to add.
        :raises TypeError: If the class is not a subclass of BaseController.
        """
        if not issubclass(controller_type, BaseController):
            raise TypeError(f"{controller_type.__name__} is not a subclass of {BaseController.__name__}")

        self.controllers.append(controller_type(self.app, self.state))

    def add_controllers(self, *controller_types: Type[BaseController]) -> None:
        """
        Adds multiple controllers to the application.

        :param controller_types: Controller classes to add.
        """
        for controller_type in controller_types:
            self.add_controller(controller_type)

    def init_controllers(self) -> None:
        """
        Initializes all registered controllers by calling their init_endpoints method.
        """
        for controller in self.controllers:
            controller.init_endpoints()

    def run_app(self, settings: RunSettings = RunSettings.get_default_prod()) -> None:
        """
        Runs the Flask application with the specified settings.

        :param settings: RunSettings object with host, port, and debug configuration.
        """
        self.app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.debug,
        )

    def add_json_provider(self, provider: DefaultJSONProvider) -> None:
        """
        Adds a custom JSON provider to the Flask application.

        :param provider: The custom JSON provider class.
        """
        self.app.json = provider

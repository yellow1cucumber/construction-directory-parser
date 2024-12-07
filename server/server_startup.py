from typing import List, Type

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from flask_cors import CORS

from pydantic import BaseModel

from server.controllers.controller_base import BaseController
from server.init_state import InitConfiguration

from server.state import ServerStateProvider


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
    """
    A class for managing the initialization and configuration of a Flask application.
    Implements a fluent API for chaining method calls to streamline server setup.

    Attributes:
        app (Flask): The Flask application instance.
        state_provider (ServerStateProvider): The provider for managing server state.
        controllers (List[BaseController]): A list of registered controllers for the application.

    Methods:
        init_server(name: str = "") -> "Startup":
            Initializes the Flask application with the given name.

        init_state() -> "Startup":
            Initializes the server state by loading configuration or creating a new state provider.

        init_cors_dev(origins=None) -> "Startup":
            Configures Cross-Origin Resource Sharing (CORS) for the development environment.

        add_controller(controller_type: Type[BaseController]) -> "Startup":
            Adds a single controller to the application.

        add_controllers(*controller_types: Type[BaseController]) -> "Startup":
            Adds multiple controllers to the application.

        init_controllers() -> "Startup":
            Initializes all registered controllers by invoking their `init_endpoints` method.

        add_json_provider(provider: DefaultJSONProvider) -> "Startup":
            Sets a custom JSON provider for the Flask application.

        run_app(settings: RunSettings = RunSettings.get_default_prod()) -> None:
            Starts the Flask application with the specified run settings.
    """

    app: Flask
    state_provider: ServerStateProvider
    controllers: List[BaseController] = []

    def init_server(self, name: str = "") -> "Startup":
        """
        Initializes the Flask application.

        Args:
            name (str): The name of the Flask application. Defaults to an empty string.

        Returns:
            Startup: The current instance for method chaining.
        """
        self.app = Flask(name)
        return self

    def init_state(self) -> "Startup":
        """
        Initializes the server state by loading it from a configuration file if available.
        If no configuration file is found, a new state provider is created.

        Returns:
            Startup: The current instance for method chaining.
        """
        config_path = InitConfiguration.find_config_path()
        if config_path:
            self.state_provider.update_state(InitConfiguration.serialize_from_file(config_path))
        else:
            self.state_provider = ServerStateProvider()
        return self

    def init_cors_dev(self, origins=None) -> "Startup":
        """
        Configures Cross-Origin Resource Sharing (CORS) for the development environment.

        Args:
            origins (list): A list of allowed origins. Defaults to allowing all origins.

        Returns:
            Startup: The current instance for method chaining.
        """
        if origins is None:
            origins = ["*"]
        CORS(self.app, resources={r"/*": {"origins": origins}})
        return self

    def add_controller(self, controller_type: Type[BaseController]) -> "Startup":
        """
        Adds a single controller to the application.

        Args:
            controller_type (Type[BaseController]): The controller class to add.

        Raises:
            TypeError: If the provided class is not a subclass of `BaseController`.

        Returns:
            Startup: The current instance for method chaining.
        """
        if not issubclass(controller_type, BaseController):
            raise TypeError(f"{controller_type.__name__} is not a subclass of {BaseController.__name__}")
        self.controllers.append(controller_type(self.app, self.state_provider))
        return self

    def add_controllers(self, *controller_types: Type[BaseController]) -> "Startup":
        """
        Adds multiple controllers to the application.

        Args:
            controller_types (Type[BaseController]): Controller classes to add.

        Returns:
            Startup: The current instance for method chaining.
        """
        for controller_type in controller_types:
            self.add_controller(controller_type)
        return self

    def init_controllers(self) -> "Startup":
        """
        Initializes all registered controllers by invoking their `init_endpoints` method.

        Returns:
            Startup: The current instance for method chaining.
        """
        for controller in self.controllers:
            controller.init_endpoints()
        return self

    def run_app(self, settings: RunSettings = RunSettings.get_default_prod()) -> None:
        """
        Starts the Flask application with the specified run settings.

        Args:
            settings (RunSettings): The settings for running the application (host, port, debug).

        Returns:
            None
        """
        self.app.run(
            host=settings.host,
            port=settings.port,
            debug=settings.debug,
        )

    def add_json_provider(self, provider: DefaultJSONProvider) -> "Startup":
        """
        Sets a custom JSON provider for the Flask application.

        Args:
            provider (DefaultJSONProvider): The custom JSON provider to use.

        Returns:
            Startup: The current instance for method chaining.
        """
        self.app.json = provider
        return self



import json
import os
from pathlib import Path
from server.state import ServerState


class InitConfiguration:
    """
    Handles the initialization and loading of server configuration files.

    Methods:
        find_config_path() -> Path | None:
            Locates the configuration file path from the environment variable `CONFIG_PATH`.

        serialize_from_file(config_file_path: Path) -> ServerState:
            Loads and parses the server state from a configuration file.
    """

    @staticmethod
    def find_config_path() -> Path | None:
        """
        Retrieves the configuration file path from the `CONFIG_PATH` environment variable.

        Returns:
            Path | None: The path to the configuration file if the environment variable is set; otherwise, None.
        """
        config_path = os.getenv('CONFIG_PATH')
        return Path(config_path) if config_path else None

    @staticmethod
    def serialize_from_file(config_file_path: Path) -> ServerState:
        """
        Loads the server configuration from a JSON file and deserializes it into a `ServerState` object.

        Args:
            config_file_path (Path): The path to the configuration file.

        Returns:
            ServerState: The deserialized server state object.

        Raises:
            FileNotFoundError: If the file does not exist.
            JSONDecodeError: If the file content is not valid JSON.
            ValidationError: If the JSON does not match the `ServerState` schema.
        """
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config_json = json.load(file)
        state: ServerState = ServerState(**config_json)
        return state

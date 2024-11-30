import json
import os
from pathlib import Path

from server.state import ServerState


class InitConfiguration:
    @staticmethod
    def find_config_path() -> Path | None:
        config_path = os.getenv('CONFIG_PATH')
        return Path(config_path) if config_path else None

    @staticmethod
    def serialize_from_file(config_file_path: Path) -> ServerState:
        with open(config_file_path, 'r', encoding='utf-8') as file:
            config_json = json.load(file)
        state: ServerState = ServerState(**config_json)
        return state
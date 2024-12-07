from flask import Flask
from flask_cors import CORS

from serialization.json_provider import CustomJSONProvider

from server.controllers.controller_base import BaseController
from server.controllers.sitemap_controller import SitemapController
from server.controllers.state_controller import StateController

from server.state import ServerState
from server.init_state import InitConfiguration

if __name__ == '__main__':
    app = Flask(__name__)
    app.json = CustomJSONProvider(app)

    CORS(app)

    state: ServerState

    config_path = InitConfiguration.find_config_path()
    if config_path:
        state = InitConfiguration.serialize_from_file(config_path)
    else:
        state = ServerState()

    controllers: [BaseController] = [
        SitemapController(app, state),
        StateController(app, state)
    ]

    for controller in controllers:
        controller.init_endpoints()

    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

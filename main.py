from serialization.json_provider import CustomJSONProvider

from server.controllers.sitemap_controller import SitemapController
from server.controllers.state_controller import StateController
from server.server_startup import Startup, RunSettings

if __name__ == '__main__':
    startup = Startup()

    startup.init_server(__name__)

    startup.init_state()

    startup.add_json_provider(CustomJSONProvider(startup.app))

    startup.init_cors_dev()

    startup.add_controllers(SitemapController, StateController)

    startup.init_controllers()

    startup.run_app(RunSettings.get_default_dev())
from serialization.json_provider import CustomJSONProvider
from server.controllers.sitemap_controller import SitemapController
from server.controllers.state_controller import StateController
from server.server_startup import Startup, RunSettings

if __name__ == '__main__':
    startup = Startup()

    startup.init_server(__name__) \
            .init_state() \
            .init_cors_dev() \
            .add_controllers(SitemapController, StateController) \
            .init_controllers()

    startup.add_json_provider(CustomJSONProvider(startup.app))

    startup.run_app(RunSettings.get_default_dev())

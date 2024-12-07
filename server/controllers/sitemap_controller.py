from flask import Flask, jsonify, request
from pydantic import ValidationError

from server.state import ServerState
from server.controllers.controller_base import BaseController

from core.extraction.sitemapExtractor import ExtractorOptions
from core.extraction.sitemap import SiteMap

from core.parsing.content_parser import ContentParser

from utils.sitemap_loading import request_sitemap_and_export
from utils.sitemap_navigation import find_page_by_id


class SitemapController(BaseController):
    def __init__(self, app: Flask, state: ServerState):
        """
        Initializes the SitemapController.

        :param app: Flask application where the endpoints will be registered.
        :param state: ServerState object containing the server's current configuration and sitemap data.
        """
        super().__init__(app, state)

    def init_endpoints(self):
        """
        Registers HTTP endpoints for managing sitemap operations.
        """
        self._app.add_url_rule(
            '/sitemap/set_extractor_options',
            view_func=self.set_extractor_options,
            methods=['POST']
        )
        self._app.add_url_rule(
            '/sitemap/request_and_export',
            view_func=self.request_and_export,
            methods=['POST']
        )
        self._app.add_url_rule(
            '/sitemap/get_page_content/<int:page_id>',
            view_func=self.get_page_content,
            methods=['GET']
        )
        self._app.add_url_rule(
            '/sitemap/get_sitemap',
            view_func=self.get_sitemap,
            methods=['GET']
        )

    def set_extractor_options(self):
        """
        Sets the options for extracting the sitemap.

        Expects a JSON payload containing the parameters matching the ExtractorOptions model.
        Returns HTTP 400 if validation fails.

        :return: JSON response indicating success or an error.
        """
        options_data = request.get_json()
        if not options_data:
            return jsonify({'error': 'Invalid or missing JSON data'}), 400

        try:
            extractor_options = ExtractorOptions(**options_data)
            self.state.extractor_options = extractor_options
            return jsonify({
                'message': 'Extractor options set successfully'
            }), 200
        except ValidationError as e:
            return jsonify({
                'error': e.errors()
            }), 400

    def request_and_export(self):
        """
        Requests the sitemap, exports it, and saves it to the server's state.

        Uses the parameters stored in `state.extractor_options`.
        Returns HTTP 400 if options are not set.

        :return: JSON response with the exported sitemap.
        """
        options = self.state.extractor_options
        if not options:
            return jsonify({'error': 'Extractor options is not set'}), 400

        sitemap = request_sitemap_and_export(
            self.state.extractor_options,
            self.state.default_sitemap_export_file
        )
        self.state.sitemap = sitemap
        self.state.extraction_file = self.state.default_sitemap_export_file

        return jsonify(sitemap), 200

    def get_sitemap(self):
        """
        Returns the current sitemap stored in the server's state.

        Returns HTTP 400 if the sitemap is not set.

        :return: JSON response with the sitemap or an error message.
        """
        sitemap = self.state.sitemap

        if not sitemap:
            return jsonify({'error': 'Sitemap is not set'}), 400
        return jsonify(sitemap), 200

    def get_page_content(self, page_id: int):
        """
        Retrieves the content of a page with the specified ID from the sitemap.

        Returns HTTP 400 if the sitemap is not set.
        Returns HTTP 404 if the page with the specified ID is not found.
        Returns HTTP 500 for any parsing errors.

        :param page_id: The ID of the page to retrieve content for.
        :return: JSON response with the page content or an error message.
        """
        sitemap: SiteMap = self.state.sitemap
        if not sitemap:
            return jsonify({'error': 'Sitemap is not set'}), 400

        page = find_page_by_id(sitemap, page_id)

        if not page:
            return jsonify({'error': f"There is no page with id == {page_id}"}), 404

        try:
            parser = ContentParser(page.url, self.state.pages_content_container_selector)
            result = parser.parse()
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

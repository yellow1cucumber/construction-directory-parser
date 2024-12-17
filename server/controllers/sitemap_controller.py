from flask import Flask, jsonify, request
from pydantic import ValidationError

from core.sitemap_extraction.category import Category
from server.state import ServerStateProvider
from server.controllers.controller_base import BaseController

from core.sitemap_extraction.sitemapExtractor import ExtractorOptions
from core.sitemap_extraction.sitemap import SiteMap

from core.content_parsing.content_parser import ContentParser
from utils.sitemap_fs import save_sitemap_to_filesystem

from utils.sitemap_loading import request_sitemap_and_export
from utils.sitemap_navigation import find_page_by_id


class SitemapController(BaseController):
    def __init__(self, app: Flask, state_provider: ServerStateProvider):
        """
        Initializes the SitemapController.

        :param app: Flask application where the endpoints will be registered.
        :param state_provider: Reactive state provider.
        """
        super().__init__(app, state_provider)

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
            '/sitemap/get_page_content/<int:page_id>/<bool:markup>',
            view_func=self.get_page_content,
            methods=['GET']
        )
        self._app.add_url_rule(
            '/sitemap/get_sitemap',
            view_func=self.get_sitemap,
            methods=['GET']
        )
        self._app.add_url_rule(
            '/sitemap/fill_sitemap_with_html',
            view_func=self.fill_sitemap_with_html,
            methods=['POST']
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
            self._state.extractor_options = extractor_options
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
        options = self._state.extractor_options
        if not options:
            return jsonify({'error': 'Extractor options is not set'}), 400

        sitemap = request_sitemap_and_export(
            self._state.extractor_options,
            self._state.default_sitemap_export_file
        )
        self._state.sitemap = sitemap
        self._state.extraction_file = self._state.default_sitemap_export_file

        return jsonify(sitemap), 200

    def get_sitemap(self):
        """
        Returns the current sitemap stored in the server's state.

        Returns HTTP 400 if the sitemap is not set.

        :return: JSON response with the sitemap or an error message.
        """
        sitemap = self._state.sitemap

        if not sitemap:
            return jsonify({'error': 'Sitemap is not set'}), 400

        return jsonify(sitemap), 200

    def get_page_content(self, page_id: int, markup: bool):
        """
        Retrieves the content of a page with the specified ID from the sitemap.

        Returns HTTP 400 if the sitemap is not set.
        Returns HTTP 404 if the page with the specified ID is not found.
        Returns HTTP 500 for any parsing errors.

        :param page_id: The ID of the page to retrieve content for.
        :param markup: If markup is true, method extracts page with html markup from container, that defined in options
        :return: JSON response with the page content or an error message.
        """
        sitemap = self._state.sitemap
        if not isinstance(sitemap, SiteMap):
            return jsonify({'error': 'Invalid sitemap format'}), 500

        if not sitemap:
            return jsonify({'error': 'Sitemap is not set'}), 400

        page = find_page_by_id(sitemap, page_id)

        if not page:
            return jsonify({'error': f"There is no page with id == {page_id}"}), 404

        try:
            parser = ContentParser(page.url, self._state.pages_content_container_selector)
            result = parser.parse(only_markup=markup)
            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    def fill_sitemap_with_html(self):
        if not self._state:
            return jsonify({'error': 'State was not set'}), 400

        if not self._state.sitemap:
            return jsonify({'error': 'Sitemap is empty'}), 400

        def process_category(target_category: Category):
            for article in target_category.articles:
                parser = ContentParser(article.url, self._state.pages_content_container_selector)
                article.html = parser.parse(only_markup=True)
            for subcategory in target_category.subcategories:
                process_category(subcategory)

        for category in self._state.sitemap.categories:
            process_category(category)

        return jsonify(self._state.sitemap), 200
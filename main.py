import json
import pprint

from flask import Flask, jsonify, request
from flask_cors import CORS
from pydantic import ValidationError

from core.extraction.sitemap import SiteMap
from core.extraction.sitemapExtractor import ExtractorOptions
from core.parsing.articleProcessor import ArticleProcessor
from core.parsing.content_parser import ContentParser
from serialization.json_provider import CustomJSONProvider
from server.state import ServerState
from utils.sitemap_loading import (import_sitemap_from_json_file,
                                   request_sitemap_and_export)
from utils.sitemap_navigation import find_page_by_id

if __name__ == '__main__':
    app = Flask(__name__)
    app.json = CustomJSONProvider(app)

    CORS(app)

    state: ServerState = ServerState()


    @app.route('/sitemap/set_extractor_options', methods=['POST'])
    def set_extractor_options():
        options_data = request.get_json()

        try:
            extractor_options = ExtractorOptions(**options_data)
            state.extractor_options = extractor_options
            return jsonify({
                'message': 'Extractor options set successfully'
            }), 200
        except ValidationError as e:
            return jsonify({
                'error': e.errors()
            }), 400


    @app.route("/sitemap/load_from_file", methods=['POST'])
    def load_from_file():
        try:
            if 'file' not in request.files:
                return jsonify({
                    'error': 'No file part in the request'
                }), 400

            sitemap_json_file = request.files['file']
            if sitemap_json_file.name == '':
                return jsonify({
                    'error': 'No selected file'
                }), 400

            if not state.extractor_options:
                return jsonify({
                    'error': 'Extractor options is not set'
                }), 400

            sitemap_json_file.save(state.default_sitemap_export_file)
            state.extraction_file = state.default_sitemap_export_file

            sitemap = import_sitemap_from_json_file(state.extractor_options,
                                                    state.extraction_file)
            state.sitemap = sitemap
            return jsonify({
                'message': 'Sitemap extracted successfully'
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500


    @app.route('/sitemap/request_and_export', methods=['POST'])
    def request_and_export():
        options = state.extractor_options
        if not options:
            return jsonify({
                'error': 'Extractor options is not set'
            }), 400

        sitemap = request_sitemap_and_export(state.extractor_options,
                                             state.default_sitemap_export_file)
        state.sitemap = sitemap
        state.extraction_file = state.default_sitemap_export_file

        return jsonify(
            sitemap
        ), 200


    @app.route('/sitemap/get_sitemap')
    def get_sitemap():
        sitemap = state.sitemap

        if not sitemap:
            return jsonify({
                'error': 'Sitemap is not set'
            }), 400
        return jsonify(sitemap), 200


    @app.route('/sitemap/get_page_content/<int:page_id>')
    def get_page_content(page_id: int):
        sitemap: SiteMap = state.sitemap
        if not sitemap:
            return jsonify({
                'error': 'Sitemap is not set'
            }), 400

        page = find_page_by_id(sitemap, page_id)

        if not page:
            return jsonify({
                'error': f"There is no page with id == {page_id}"
            })

        try:
            parser = ContentParser(page.url, 'div.page_text')
            result = parser.parse()
            return jsonify(result), 200

        except Exception as e:
            return jsonify({
                'error': str(e)
            }), 500


    @app.route('/state/export_state')
    def export_state():
        return jsonify(state.model_dump())


    @app.route('/state/import_state', methods=['POST'])
    def import_state():
        state_data = request.get_json()

        try:
            global state
            state = ServerState(**state_data)

            return jsonify({
                'message': 'State imported successfully'
            }), 200

        except Exception as e:
            return jsonify({
                'error': str(e)
            })


    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )

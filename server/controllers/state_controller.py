from requests import request

from flask import Flask, jsonify, request
from pydantic import ValidationError

from server.state import ServerState
from server.controllers.controller_base import BaseController


class StateController(BaseController):
    def __init__(self, app: Flask, state: ServerState):
        """
        Initializes the StateController.

        :param app: Flask application where the endpoints will be registered.
        :param state: Current state of the server.
        """
        super().__init__(app, state)

    def init_endpoints(self):
        """
        Registers HTTP endpoints for state operations.
        """
        self._app.add_url_rule('/state/export_state',
                                view_func=self.export_state,
                                methods=['GET'])
        self._app.add_url_rule('/state/import_state',
                                view_func=self.import_state,
                                methods=['POST'])

    def export_state(self):
        """
        Exports the current server state.

        :return: JSON response with the serialized server state.
        """
        return jsonify(self.state.model_dump())  # Use model_dump if state supports it

    def import_state(self):
        """
        Imports the server state from a JSON payload.

        Expects:
        {
            "field1": "value1",
            "field2": "value2",
            ...
        }

        :return: JSON response with a success or error message.
        """
        state_data = request.get_json()
        if not state_data:
            return jsonify({'error': 'Invalid or missing JSON data'}), 400

        try:
            self.state = ServerState(**state_data)
            return jsonify({'message': 'State imported successfully'}), 200
        except ValidationError as e:
            return jsonify({'error': e.errors()}), 400
        except Exception as e:
            return jsonify({'error': str(e)}), 500

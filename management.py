import sqlite3
import bpcommon
import flask
from jsonschema import validate, ValidationError
from flask import Flask, request, jsonify
management = Flask(__name__)

DATABASE = None

# TODO: put in another file?
NEW_PET_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string"
        },
        "strength": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "agility": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "wit": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        },
        "senses": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
        }
    },
    "required": ["name", "strength", "agility", "wit", "senses"]
}

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
class InvalidUsage(Exception):

    status_code = 400

    def __init__(self, message, payload = None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    def to_dict(self):
        d = dict(self.payload or ())
        d['message'] = self.message
        return d


# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@management.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@management.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

@management.route("/new-pet", methods=["POST"])
def new_pet():

    # Setting silent=True causes get_json to return None on error, instead
    # of calling on_json_loading_failed. The latter case is undesirable because
    # it leads to an HTML error message, whereas we want to produce JSON
    # error messages.
    request_data = request.get_json(silent = True)

    if request_data == None:
        raise InvalidUsage("No JSON object could be decoded") 

    try:
        validate(request_data, NEW_PET_REQUEST_SCHEMA)
    except ValidationError:
        message = "Your JSON post does not match NEW_PET_REQUEST_SCHEMA."
        schema = {"NEW_PET_REQUEST_SCHEMA" : NEW_PET_REQUEST_SCHEMA}
        raise InvalidUsage(message, schema) 

    return str(request_data)

# TODO: arguments from command line
if __name__ == "__main__":
    DATABASE = "test.db"
    management.run()

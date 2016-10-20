import sqlite3
import bpcommon
import flask
from jsonschema import validate, ValidationError
from flask import Flask, request
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





# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@management.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

@management.route("/new-pet", methods=["POST"])
def new_pet():

    ## TODO: Return errors (eg 400) as JSON?
    request_data = request.get_json()

    if request_data == None:
        request.on_json_loading_failed("No JSON object could be decoded")

    try:
        validate(request_data, NEW_PET_REQUEST_SCHEMA)
    except ValidationError:
        request.on_json_loading_failed("Your JSON post was valid JSON, " +
            "however it does not match NEW_PET_REQUEST_SCHEMA")

    return str(request_data)

# TODO: arguments from command line
if __name__ == "__main__":
    DATABASE = "test.db"
    management.run()

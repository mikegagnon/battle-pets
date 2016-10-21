# TODO: cleanup imports

import sqlite3
import bpcommon
import flask
from jsonschema import validate, ValidationError
from flask import Flask, request, jsonify
app = Flask(__name__)

app.config['DATABASE'] = "database.db"

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

def init_db():
    conn = get_db()

    cursor = conn.cursor()

    # TODO: uniq names? ids?
    # Create table
    cursor.execute('''CREATE TABLE Animals
                 (name text,
                 strength real,
                 agility real,
                 wit real,
                 senses real)''')

    # Save (commit) the changes
    conn.commit()

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

# TODO: rename vars
# TODO: limit animal name length
@app.route("/new-pet", methods=["POST"])
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

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name from Animals where name = ?;",
        (request_data["name"], ))

    data = cursor.fetchone()

    app.logger.debug(data)

    response = None

    # If this is a new animal
    if data == None:
        cursor.execute('''
            INSERT INTO Animals(name, strength, agility, wit, senses)
            VALUES (?, ?, ?, ?, ?);''',
            (request_data["name"],
            request_data["strength"],
            request_data["agility"],
            request_data["wit"],
            request_data["senses"]))

        conn.commit()

        response = {
            "success": True
        }

    else:

        # TODO: escape animal name?
        response = {
            "success": False,
            "message": "A pet with the name '%s' already exists." %
                request_data["name"]
        }

    return flask.jsonify(**response)

# TODO: arguments from command line
if __name__ == "__main__":
    app.run()

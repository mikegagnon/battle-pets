# TODO: cleanup imports

import sqlite3
import argparse
import bpcommon
import flask
from jsonschema import validate, ValidationError
from flask import Flask, request, jsonify, json

app = Flask(__name__)

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
class RestError(Exception):

    def __init__(self, message, payload = None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    def to_dict(self):
        d = dict(self.payload or ())
        d['message'] = self.message
        return d

class InvalidUsage(RestError):
    status_code = 400

class NotFound(RestError):
    status_code = 404

def init_db():

    conn = sqlite3.connect(app.config['DATABASE'])

    cursor = conn.cursor()

    # TODO: uniq names? ids?
    # Create table
    cursor.execute('''CREATE TABLE Animals
                 (name text PRIMARY KEY,
                 strength real,
                 agility real,
                 wit real,
                 senses real)''')

    # Save (commit) the changes
    conn.commit()

    conn.close()

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
def get_db():
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(app.config['DATABASE'])
    return db

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@app.errorhandler(InvalidUsage)
@app.errorhandler(NotFound)
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
# TODO: limit animal attributes
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

        return ''

    else:
        raise InvalidUsage("A pet with the name '%s' already exists." %
            request_data["name"])


@app.route("/get-pet/<string:petname>", methods=["GET"])
def get_pet(petname):

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name, strength, agility, wit, senses from " +
        "Animals where name = ?;", (petname, ))

    data = cursor.fetchone()

    # If this is a new animal
    if data == None:
        raise NotFound("A pet with the name '%s' does not exist." % petname)
    else:
        response = {
                "name": data[0],
                "strength": data[1],
                "agility": data[2],
                "wit": data[3],
                "senses": data[4],
            }
        return json.dumps(response)

# TODO: arguments from command line
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='management.py')

    parser.add_argument('--db', nargs='?', help='Filename for the database',
        default="database.db", dest="database_filename")
    parser.add_argument('--init_db', action='store_true', dest="init_db",
        help="Initialize a database")

    args = parser.parse_args()

    app.config['DATABASE'] = args.database_filename

    if args.init_db:
        init_db()
    else:
        app.run()

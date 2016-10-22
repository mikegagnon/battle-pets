import argparse
import bpcommon
import flask
import jsonschema
import sqlite3

app = flask.Flask(__name__)

MAX_PET_NAME_LENGTH = 100

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

    cursor.execute('''CREATE TABLE Pets
                 (name TEXT,
                 strength REAL,
                 agility REAL,
                 wit REAL,
                 senses REAL)''')

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
def handle_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

# The sum of the attributes must be <= 1.0
def valid_new_pet(pet):
    return  len(pet["name"]) <= MAX_PET_NAME_LENGTH and \
        (pet["strength"] +
        pet["agility"] +
        pet["wit"] +
        pet["senses"]) <= 1.0

# TODO: limit animal name length
@app.route("/new-pet", methods=["POST"])
def new_pet():

    # Setting silent=True causes get_json to return None on error, instead
    # of calling on_json_loading_failed. The latter case is undesirable because
    # it leads to an HTML error message, whereas we want to produce JSON
    # error messages.
    request_data = flask.request.get_json(silent = True)

    if request_data == None:
        raise InvalidUsage("No JSON object could be decoded") 

    try:
        jsonschema.validate(request_data, NEW_PET_REQUEST_SCHEMA)
    except jsonschema.ValidationError:
        message = "Your JSON post does not match NEW_PET_REQUEST_SCHEMA."
        schema = {"NEW_PET_REQUEST_SCHEMA" : NEW_PET_REQUEST_SCHEMA}
        raise InvalidUsage(message, schema) 

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Pets WHERE name = ?;",
        (request_data["name"], ))

    # TODO: change data to pet
    data = cursor.fetchone()

    # If this is a new pet
    if data == None:

        if valid_new_pet(request_data):

            cursor.execute('''
                INSERT INTO Pets(name, strength, agility, wit, senses)
                VALUES (?, ?, ?, ?, ?);''',
                (request_data["name"],
                request_data["strength"],
                request_data["agility"],
                request_data["wit"],
                request_data["senses"]))

            conn.commit()

            return ''

        else:
            message = "The sum of (strength, agility, wit, senses) must be " + \
                "<= 1.0 AND the length of name must be <= %s." % \
                MAX_PET_NAME_LENGTH

            raise InvalidUsage(message)

    else:
        raise InvalidUsage("A pet with the name '%s' already exists." %
            request_data["name"])


@app.route("/get-pet/<string:petname>", methods=["GET"])
def get_pet(petname):

    if len(petname) > MAX_PET_NAME_LENGTH:
        message = "The name of the pet must be <= %s" % MAX_PET_NAME_LENGTH

        raise InvalidUsage(message)

    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT name, strength, agility, wit, senses FROM " +
        "Pets where name = ?;", (petname, ))

    data = cursor.fetchone()

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
        return flask.json.dumps(response)

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

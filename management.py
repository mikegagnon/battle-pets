import argparse
import flask
import jsonschema
import sqlite3

import db
import error
import validation

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
@app.errorhandler(error.InvalidUsage)
@app.errorhandler(error.NotFound)
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

def valid_pet_name(petname):
    return len(petname) <= MAX_PET_NAME_LENGTH

# The sum of the attributes must be <= 1.0
def valid_new_pet(pet):
    return  valid_pet_name(pet["name"]) and \
        (pet["strength"] +
        pet["agility"] +
        pet["wit"] +
        pet["senses"]) <= 1.0

# TODO: get rid of nested ifs
@app.route("/new-pet", methods=["POST"])
def new_pet():

    request_data = validation.validate_json("NEW_PET_REQUEST_SCHEMA",
        NEW_PET_REQUEST_SCHEMA)

    conn = db.get_db(app)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM Pets WHERE name = ?;",
        (request_data["name"], ))

    pet = cursor.fetchone()

    if pet != None:
        raise error.InvalidUsage("A pet with the name '%s' already exists." %
            request_data["name"])

    if not valid_new_pet(request_data):
        message = "The sum of (strength, agility, wit, senses) must be " + \
            "<= 1.0 AND the length of name must be <= %s." % \
            MAX_PET_NAME_LENGTH

        raise error.InvalidUsage(message)

    cursor.execute('''
        INSERT INTO Pets(name, strength, agility, wit, senses, wins, losses,
            experience)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?);''',
        (request_data["name"],
        request_data["strength"],
        request_data["agility"],
        request_data["wit"],
        request_data["senses"],
        0, 0, 0))

    conn.commit()

    return ''

@app.route("/get-pet/<string:petname>", methods=["GET"])
def get_pet(petname):

    if not valid_pet_name(petname):
        message = "The name of the pet must be <= %s" % MAX_PET_NAME_LENGTH

        raise error.InvalidUsage(message)

    conn = db.get_db(app)
    cursor = conn.cursor()

    cursor.execute("SELECT name, strength, agility, wit, senses, wins, " +
        "losses, experience FROM Pets where name = ?;", (petname, ))

    data = cursor.fetchone()

    if data == None:
        raise error.NotFound("A pet with the name '%s' does not exist." %
            petname)

    # TODO: rm else
    else:
        response = {
                "name": data[0],
                "strength": data[1],
                "agility": data[2],
                "wit": data[3],
                "senses": data[4],
                "wins": data[5],
                "losses": data[6],
                "experience": data[7]
            }
        return flask.json.dumps(response)

# TODO: arguments from command line
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='management.py')

    parser.add_argument('--db', nargs='?', help='Filename for the database',
        default="database.db", dest="database_filename")

    parser.add_argument('--port', nargs='?', help="The port to run the " + \
        "server on", default=5000, dest="port", type=int)

    args = parser.parse_args()

    app.config['DATABASE'] = args.database_filename

    app.run("0.0.0.0", args.port)

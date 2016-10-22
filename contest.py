import argparse
import flask
import jsonschema
import redis
import rq

import battle
import db
import error
import validation

app = flask.Flask(__name__)

queue = rq.Queue(connection=redis.Redis())

CONTEST_SCHEMA = {
    "type": "array",
    "items": {
        "type": "string"
    }
}

ONE_DAY = 86400

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@app.errorhandler(error.InvalidUsage)
@app.errorhandler(error.NotFound)
@app.errorhandler(error.Processing)
def handle_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

# TODO: do not allow the same pet to battle itself
# TODO: document
@app.route("/contest", methods=["POST"])
def contest():

    request_data = validation.validate_json("CONTEST_SCHEMA", CONTEST_SCHEMA)

    assert(type(request_data) is list)

    if len(request_data) != 2:
        message = "The request must be a JSON array with two pet names."
        raise error.InvalidUsage(message)

    conn = db.get_db(app)
    cursor = conn.cursor()

    cursor.execute("SELECT name, strength, agility, wit, senses FROM Pets " + \
        "WHERE name = ? or name = ?;",
        (request_data[0], request_data[1]))

    # TODO: change data to pet
    pets = cursor.fetchall()

    # TODO: find which petname(s) is/are missing
    if len(pets) != 2:
        message = "One or more of the pets you specified do not exist."
        raise error.InvalidUsage(message)

    job = queue.enqueue(battle.do_battle, pets, result_ttl=ONE_DAY, ttl=ONE_DAY)

    return flask.json.dumps(job.id)

@app.route("/contest-result/<string:jobid>", methods=["GET"])
def contest_result(jobid):

    job = queue.fetch_job(jobid)

    if job.result == None:
        raise error.Processing("The server is still processing this battle.")

    return flask.json.dumps(job.result)


# TODO: factor out common code
if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='management.py')

    parser.add_argument('--db', nargs='?', help='Filename for the database',
        default="database.db", dest="database_filename")

    parser.add_argument('--port', nargs='?', help="The port to run the " + \
        "server on", default=5001, dest="port", type=int)

    args = parser.parse_args()

    app.config['DATABASE'] = args.database_filename

    app.run("0.0.0.0", args.port)

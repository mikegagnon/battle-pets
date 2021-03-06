import argparse
import flask
import redis
import rq

import battle
import db
import error
import validation

app = flask.Flask(__name__)

redis_conn = redis.Redis()
queue = rq.Queue(connection=redis_conn)
failed_queue = rq.get_failed_queue(connection=redis_conn)

CONTEST_SCHEMA = {
    "type": "object",
    "properties": {
        "name1": {
            "type": "string"
        },
        "name2": {
            "type": "string"
        },
        "category": {
            "enum": ["strength", "agility", "wit", "senses"]
        }
    },
    "required": ["name1", "name2", "category"]
}

# Number of seconds in a day
ONE_DAY = 86400

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(flask.g, '_database', None)
    if db is not None:
        db.close()

# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
@app.errorhandler(error.InvalidUsage)
@app.errorhandler(error.Processing)
@app.errorhandler(error.InternalServerError)
@app.errorhandler(error.NotFound)
def handle_error(error):
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

def battlePetFromRow(row):
    return battle.BattlePet(row[0], row[1], row[2], row[3], row[4], row[5],
        row[6], row[7], row[8])

@app.route("/arena", methods=["POST"])
def arena():

    request_data = validation.validate_json(flask.request, "CONTEST_SCHEMA",
        CONTEST_SCHEMA)

    conn = db.get_db(app)
    cursor = conn.cursor()

    cursor.execute("SELECT name, strength, agility, wit, senses, wins, " +
        "losses, experience, rowid FROM Pets WHERE name = ? or name = ?;",
        (request_data["name1"], request_data["name2"]))

    pet_rows = cursor.fetchall()

    if len(pet_rows) != 2:
        message = "One or more of the pets you specified do not exist, or " + \
            "you have specified that the same pet fight itself"
        raise error.InvalidUsage(message)

    pet1 = battlePetFromRow(pet_rows[0])
    pet2 = battlePetFromRow(pet_rows[1])

    try:
        job = queue.enqueue(battle.do_battle_db, pet1, pet2,
            request_data["category"], app.config['BATTLE_TIME'],
            app.config['DATABASE'], result_ttl=ONE_DAY, ttl=ONE_DAY)
    except redis.ConnectionError:
        message = "There was an internal server error."
        raise error.InternalServerError(message)

    return flask.json.dumps(job.id)

@app.route("/arena-result/<string:jobid>", methods=["GET"])
def arena_result(jobid):

    try:
        failed_job = failed_queue.fetch_job(jobid)
    except redis.ConnectionError:
        message = "There was an internal server error."
        raise error.InternalServerError(message)

    if failed_job == None:
        raise error.NotFound("Could not find a contest for that job ID")
    elif failed_job.is_failed:
        raise error.InternalServerError("There was an error in the server. " +
            "The job has failed.")

    try:
        job = queue.fetch_job(jobid)
    except redis.ConnectionError:
        message = "There was an internal server error."
        raise error.InternalServerError(message)

    if job.result == None:
        raise error.Processing("The server is still processing this battle.")

    victor = job.result
    return flask.json.dumps(victor)

@app.route("/history", methods=["GET"])
def history():

    conn = db.get_db(app)
    cursor = conn.cursor()

    cursor.execute('''SELECT victor, second_place, category, battle_timestamp
                      FROM History''')

    rows = cursor.fetchall()

    return flask.json.dumps(rows)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='management.py')

    parser.add_argument('--db', nargs='?', help='Filename for the database',
        default="database.db", dest="database_filename")

    parser.add_argument('--port', nargs='?', help="The port to run the " + \
        "server on", default=5001, dest="port", type=int)

    parser.add_argument('--battle_time', nargs='?',
        help="Length of time (in seconds) for each battle",
        default=1, dest="battle_time", type=float)

    args = parser.parse_args()

    app.config['DATABASE'] = args.database_filename
    app.config['BATTLE_TIME'] = args.battle_time

    app.run("0.0.0.0", args.port)

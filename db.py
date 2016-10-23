import argparse
import flask
import sqlite3

# TODO: rm
app = flask.Flask(__name__)

def init_db(app):

    conn = sqlite3.connect(app.config['DATABASE'])

    cursor = conn.cursor()

    cursor.execute('''CREATE TABLE Pets
                 (name TEXT,
                 strength REAL,
                 agility REAL,
                 wit REAL,
                 senses REAL,
                 wins INT,
                 losses INT,
                 experience INT);''')

    cursor.execute('''CREATE TABLE History
                 (victor TEXT,
                  second_place TEXT,
                  battle_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    NOT NULL);''')

    conn.commit()

    conn.close()

# from http://flask.pocoo.org/docs/0.11/patterns/sqlite3/
def get_db(app):
    db = getattr(flask.g, '_database', None)
    if db is None:
        db = flask.g._database = sqlite3.connect(app.config['DATABASE'])
    return db

if __name__ == "__main__":

    parser = argparse.ArgumentParser(prog='db.py')

    parser.add_argument('--db', nargs='?', help='Filename for the database',
        default="database.db", dest="database_filename")

    args = parser.parse_args()

    app.config['DATABASE'] = args.database_filename

    init_db(app)

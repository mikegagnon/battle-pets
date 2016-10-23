
# TODO: cleanup imports
from flask import json
import os
import rq
import tempfile
import unittest

import contest
import db
import test_management

import time

BATTLE_TIME = 0.2
POLL_SLEEP_TIME = 0.1

# from http://flask.pocoo.org/docs/0.11/testing/

class ContestTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, contest.app.config['DATABASE'] = tempfile.mkstemp()
        contest.app.config['BATTLE_TIME'] = BATTLE_TIME

        contest.app.config['TESTING'] = True
        self.app = contest.app.test_client()
        self.app.debug = True
        with contest.app.app_context():
            db.init_db(contest.app)

            conn = db.get_db(contest.app)
            cursor = conn.cursor()

            # Populate the database
            cursor.execute('''
                INSERT INTO Pets(name, strength, agility, wit, senses)
                VALUES ("foo", 0.25, 0.25, 0.25, 0.25);''')
            
            cursor.execute('''
                INSERT INTO Pets(name, strength, agility, wit, senses)
                VALUES ("bar", 0.25, 0.25, 0.25, 0.25);''')

            conn.commit()


    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(contest.app.config['DATABASE'])

    def test_contest_and_result(self):
        request_data = {
                "name1": "foo",
                "name2": "bar",
                "category": "strength"
            }

        response = self.app.post('/contest', data=json.dumps(request_data),
            content_type='application/json')

        assert response.status == "200 OK"

        job_id = json.loads(response.data)
        assert len(job_id) == 36

        response = self.app.get('/contest-result/' + job_id)

        while response.status == "102 PROCESSING":
            time.sleep(POLL_SLEEP_TIME)
            response = self.app.get('/contest-result/' + job_id)

if __name__ == '__main__':
    unittest.main()

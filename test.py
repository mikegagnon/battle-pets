
# TODO: cleanup imports
from flask import json
import os
import management
import unittest
import tempfile
import time

import db
import contest
import battle

# TODO: put in another file?
def post_new_pet(app, name, agility, senses, strength, wit):
    request_data = json.dumps(
        {
          "name": name,
          "strength": strength,
          "agility": agility,
          "wit": wit,
          "senses": senses,
        })

    # This succeeds because foo is a new pet
    rv = app.post('/new-pet', data=request_data,
        content_type='application/json')

    return rv

# from http://flask.pocoo.org/docs/0.11/testing/
class ManagementTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, management.app.config['DATABASE'] = tempfile.mkstemp()
        management.app.config['TESTING'] = True
        self.app = management.app.test_client()
        self.app.debug = True
        with management.app.app_context():
            db.init_db(management.app)

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(management.app.config['DATABASE'])

    def test_new_pet_duplicate(self):

        response = post_new_pet(self.app, "foo", 0.25, 0.25, 0.25, 0.25)
        assert response.status == "200 OK"
        assert response.data == ""

        # This fails because there is already a pet named foo
        response = post_new_pet(self.app, "foo", 0.25, 0.25, 0.25, 0.25)
        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data) == {
                "message": "A pet with the name 'foo' already exists."
            }

    def test_new_pet_no_json(self):

        request_data = "abc"

        response = self.app.post('/new-pet', data=request_data,
            content_type='application/json')

        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data) == {
                "message": "No JSON object could be decoded"
            }

    def test_new_pet_bad_schema(self):

        request_data = json.dumps(
            {
              "name": "foo"
            })

        # This succeeds because foo is a new pet
        response = self.app.post('/new-pet', data=request_data,
            content_type='application/json')

        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "Your JSON post does not match NEW_PET_REQUEST_SCHEMA."

    def test_new_pet_bad_attributes(self):

        response = post_new_pet(self.app, "foo", 0.25, 0.25, 0.25, 0.2500001)
        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "The sum of (strength, agility, wit, senses) must be <= 1.0 " + \
            "AND the length of name must be <= %s." % \
            management.MAX_PET_NAME_LENGTH

    def test_new_pet_bad_name(self):
        length = 1 + management.MAX_PET_NAME_LENGTH
        response = post_new_pet(self.app, "X" * length, 0.2, 0.2, 0.2, 0.2)
        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "The sum of (strength, agility, wit, senses) must be <= 1.0 " + \
            "AND the length of name must be <= %s." % \
            management.MAX_PET_NAME_LENGTH

    def test_new_pet_good_name(self):

        length = management.MAX_PET_NAME_LENGTH
        response = post_new_pet(self.app, "X" * length, 0.2, 0.2, 0.2, 0.2)
        assert response.status == "200 OK"
        assert response.data == ""

    def test_get_pet_success(self):

        # First, add foo to the database
        response = post_new_pet(self.app, "foo", 0.25, 0.25, 0.25, 0.25)
        assert response.status == "200 OK"
        assert response.data == ""

        response = self.app.get("get-pet/foo")
        assert response.status == "200 OK"
        assert json.loads(response.data) == {
                "name": "foo",
                "strength": 0.25,
                "agility": 0.25,
                "wit": 0.25,
                "senses": 0.25,
                "wins": 0,
                "losses": 0,
                "experience": 0,
            }

    def test_get_pet_failure(self):

        response = self.app.get("get-pet/foo")

        assert response.status == "404 NOT FOUND"
        assert json.loads(response.data) == {
                "message": "A pet with the name 'foo' does not exist."
            }

# To test contest_result's ability to handle failed jobs, just add
# raise ValueError("x") to the top of do_battle in battle.py
#
# Then you will see a failed assertion:
#       assert response.status != "500 INTERNAL SERVER ERROR"
# for the test_contest_result test case
#
# I couldn't find a more elegant way to test for this case.
#

class ContestTestCase(unittest.TestCase):

    BATTLE_TIME = 0.2
    POLL_SLEEP_TIME = 0.1

    def setUp(self):
        self.db_fd, contest.app.config['DATABASE'] = tempfile.mkstemp()
        contest.app.config['BATTLE_TIME'] = ContestTestCase.BATTLE_TIME

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

    def test_contest_no_json(self):
        request_data = "this is not json"

        response = self.app.post('/contest', data=request_data,
            content_type='application/json')

        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data) == {
                "message": "No JSON object could be decoded"
            }

    def test_contest_fail_schema(self):
        request_data = {
                "name1": "foo",
                "name2": "bar",
                "category": "this will cause an error"
            }

        response = self.app.post('/contest', data=json.dumps(request_data),
            content_type='application/json')

        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "Your JSON post does not match CONTEST_SCHEMA."

    def submit_contest(self):
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

        return job_id

    def test_contest(self):
        self.submit_contest()

    def test_contest_result(self):
        job_id = self.submit_contest()

        response = self.app.get('/contest-result/' + job_id)

        while response.status == "102 PROCESSING":
            time.sleep(ContestTestCase.POLL_SLEEP_TIME)
            response = self.app.get('/contest-result/' + job_id)

        assert response.status != "500 INTERNAL SERVER ERROR"

        response_json = json.loads(response.data)

        assert response_json["victor"] == "foo"
        assert response_json["2nd place"] == "bar"

class BattleTestCase(unittest.TestCase):

    def test_battle(self):
        pass

if __name__ == '__main__':
    unittest.main()

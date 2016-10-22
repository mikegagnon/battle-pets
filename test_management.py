
from flask import json
import os
import management
import unittest
import tempfile

# from http://flask.pocoo.org/docs/0.11/testing/

class ManagementTestCase(unittest.TestCase):

    def setUp(self):
        self.db_fd, management.app.config['DATABASE'] = tempfile.mkstemp()
        management.app.config['TESTING'] = True
        self.app = management.app.test_client()
        self.app.debug = True
        with management.app.app_context():
            management.init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(management.app.config['DATABASE'])

    def post_new_pet(self, name, agility, senses, strength, wit):
        request_data = json.dumps(
            {
              "name": name,
              "strength": strength,
              "agility": agility,
              "wit": wit,
              "senses": senses,
            })

        # This succeeds because foo is a new pet
        rv = self.app.post('/new-pet', data=request_data,
            content_type='application/json')

        return rv

    def test_new_pet_duplicate(self):

        response = self.post_new_pet("foo", 0.25, 0.25, 0.25, 0.25)
        assert response.status == "200 OK"
        assert response.data == ""

        # This fails because there is already a pet named foo
        response = self.post_new_pet("foo", 0.25, 0.25, 0.25, 0.25)
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

        response = self.post_new_pet("foo", 0.25, 0.25, 0.25, 0.2500001)
        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "The sum of (strength, agility, wit, senses) must be <= 1.0 " + \
            "AND the length of name must be <= %s." % \
            management.MAX_PET_NAME_LENGTH

    def test_new_pet_bad_name(self):
        length = 1 + management.MAX_PET_NAME_LENGTH
        response = self.post_new_pet("X" * length, 0.2, 0.2, 0.2, 0.2)
        assert response.status == "400 BAD REQUEST"
        assert json.loads(response.data)["message"] == \
            "The sum of (strength, agility, wit, senses) must be <= 1.0 " + \
            "AND the length of name must be <= %s." % \
            management.MAX_PET_NAME_LENGTH

    def test_new_pet_good_name(self):

        length = management.MAX_PET_NAME_LENGTH
        response = self.post_new_pet("X" * length, 0.2, 0.2, 0.2, 0.2)
        assert response.status == "200 OK"
        assert response.data == ""

    def test_get_pet_success(self):

        # First, add foo to the database
        response = self.post_new_pet("foo", 0.25, 0.25, 0.25, 0.25)
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
            }

    def test_get_pet_failure(self):

        response = self.app.get("get-pet/foo")

        assert response.status == "404 NOT FOUND"
        assert json.loads(response.data) == {
                "message": "A pet with the name 'foo' does not exist."
            }


if __name__ == '__main__':
    unittest.main()

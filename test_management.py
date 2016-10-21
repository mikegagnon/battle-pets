
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

    # TODO: reduce code duplication
    def test_new_pet(self):

        # This succeeds because foo is a new pet
        rv = self.app.post('/new-pet', data=json.dumps(
            {
              "name": "foo",
              "agility": 0.5,
              "senses": 0.5,
              "strength": 0.5,
              "wit": 0.5
            }),
            content_type='application/json')

        assert json.loads(rv.data) == {"success": True}

        # This fails because there is already a pet named foo
        rv = self.app.post('/new-pet', data=json.dumps(
            {
              "name": "foo",
              "agility": 0.5,
              "senses": 0.5,
              "strength": 0.5,
              "wit": 0.5
            }),
            content_type='application/json')

        print rv.data

if __name__ == '__main__':
    unittest.main()
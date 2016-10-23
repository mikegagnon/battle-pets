
# from http://flask.pocoo.org/docs/0.11/patterns/apierrors/
class RestError(Exception):

    def __init__(self, message, payload = None):
        Exception.__init__(self)
        self.message = message
        self.payload = payload

    def to_dict(self):
        d = dict(self.payload or ())
        d["message"] = self.message
        return d

class InvalidUsage(RestError):
    status_code = 400

class NotFound(RestError):
    status_code = 404

class Processing(RestError):
    status_code = 102

class InternalServerError(RestError):
    status_code = 500

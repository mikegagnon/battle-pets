import flask
import jsonschema

import error

# TODO: move lask.request.get_json(silent = True) into caller, not here
def validate_json(schema_name, schema):

    # Setting silent=True causes get_json to return None on error, instead
    # of calling on_json_loading_failed. The latter case is undesirable because
    # it leads to an HTML error message, whereas we want to produce JSON
    # error messages.
    request_data = flask.request.get_json(silent = True)

    if request_data == None:
        raise error.InvalidUsage("No JSON object could be decoded") 

    try:
        jsonschema.validate(request_data, schema)
    except jsonschema.ValidationError:
        message = "Your JSON post does not match %s." % schema_name
        schema = {schema_name : schema}
        raise error.InvalidUsage(message, schema) 

    return request_data

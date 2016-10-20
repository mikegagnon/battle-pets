from string import Template
import flask

# TODO

ERROR_MISSING_JSON_INPUT = 1

def invalid_json(url):
    template = Template("Error: You may only access $url by POSTing JSON.")
    message = template.substitute(url=url)
    return error_json(ERROR_MISSING_JSON_INPUT, message)

def error_json(code, message):
    return flas.jsonify({
            "error-code": code,
            "message": message
        })

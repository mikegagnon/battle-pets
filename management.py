from flask import Flask, request
management = Flask(__name__)

@management.route("/new-pet", methods=["POST"])
def new_pet():
    request_data = request.get_json()
    return str(request_data)

if __name__ == "__main__":
    management.run()
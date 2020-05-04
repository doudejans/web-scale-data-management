import uuid

from flask import Flask, jsonify, make_response

app = Flask(__name__)


# returns an ID
@app.route("/create", methods=["POST"])
def create_user():
    # TODO
    my_uuid = uuid.uuid4()
    return make_response(str(my_uuid), 201)


# return success/failure
@app.route("/remove/<uuid:user_id>", methods=["DELETE"])
def remove_user(user_id):
    # TODO
    success = True
    if success:
        return make_response('success', 200)
    else:
        return make_response('failure', 500)


# returns a set of users with their details (id, and credit)
@app.route("/find/<uuid:user_id>", methods=["GET"])
def find_user(user_id):
    # TODO
    credit = 0
    success = True
    if success:
        return make_response(jsonify(id=user_id, credit=credit), 200)
    else:
        return make_response('user_id not found', 404)


# returns the current credit of a user
@app.route("/credit/<uuid:user_id>", methods=["GET"])
def get_credit(user_id):
    # TODO
    credit = 0
    success = True
    if success:
        return make_response(str(credit), 200)
    else:
        return make_response('failure', 500)


# subtracts the amount from the credit of the user (e.g., to buy an order). Returns success or failure, depending on the credit status.
@app.route("/credit/subtract/<uuid:user_id>/<int:amount>", methods=["POST"])
def credit_subtract(user_id, amount):
    # TODO
    success = True
    if success:
        return make_response('success', 200)
    else:
        return make_response('failure', 500)


# adds the amount from the credit of the user. Returns success or failure, depending on the credit status.
@app.route("/credit/add/<uuid:user_id>/<int:amount>", methods=["POST"])
def credit_add(user_id, amount):
    # TODO
    success = True
    if success:
        return make_response('success', 200)
    else:
        return make_response('failure', 500)


if __name__ == '__main__':
    app.run()

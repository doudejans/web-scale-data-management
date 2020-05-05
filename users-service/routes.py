from flask import Flask, jsonify, make_response
from database.database import Database
from http import HTTPStatus
import uuid

# This is the main file of the service, handling with the different routes
# the microservice exposes.


# The db variable here can be either 'db_postgres.py' or 'db_cassandra.py'
# based on the config given to the application.
def create_app(db: Database):
    service = Flask(__name__)
    # The db variable will be set by app.py to either cassandra or postgres
    # depending on flags used when starting the application. You can assume

    @service.route('/health')
    def health():
        return jsonify({"status": "ok", "database": db.DATABASE})

    # Define the route from the point where it is unique,
    # so '/users/create' ->
    # '/create'. The '/users' part will be handled by the proxy.
    @service.route('/create')
    def create_x():
        # I have implemented this example route using the example query
        # present in both the cassandra and postgres database.
        return jsonify({"version": db.retrieve_version()})

    # TODO: Add the microservice routes here...
    # returns an ID
    @service.route("/create", methods=["POST"])
    def create_user():
        my_uuid = db.create_user()
        if uuid is not None:
            return make_response(my_uuid, HTTPStatus.CREATED)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # return success/failure
    @service.route("/remove/<uuid:user_id>", methods=["DELETE"])
    def remove_user(user_id):
        success = db.remove_user(user_id)
        if success:
            return make_response('success', HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # returns a set of users with their details (id, and credit)
    @service.route("/find/<uuid:user_id>", methods=["GET"])
    def find_user(user_id):
        # TODO
        credit = 0
        success = True
        if success:
            return make_response(jsonify(id=user_id, credit=credit), HTTPStatus.OK)
        else:
            return make_response('user_id not found', HTTPStatus.NOT_FOUND)

    # returns the current credit of a user
    @service.route("/credit/<uuid:user_id>", methods=["GET"])
    def get_credit(user_id):
        # TODO
        credit = db.get_credit(user_id)
        if credit is not None:
            return make_response(str(credit), HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.NOT_FOUND)

    # subtracts the amount from the credit of the user (e.g., to buy an order). Returns success or failure, depending on the credit status.
    @service.route("/credit/subtract/<uuid:user_id>/<int:amount>", methods=["POST"])
    def credit_subtract(user_id, amount):
        success = db.credit_subtract(user_id, amount)
        if success:
            return make_response('success', HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # adds the amount from the credit of the user. Returns success or failure, depending on the credit status.
    @service.route("/credit/add/<uuid:user_id>/<int:amount>", methods=["POST"])
    def credit_add(user_id, amount):
        success = db.credit_add(user_id, amount)
        if success:
            return make_response('success', HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)


    return service


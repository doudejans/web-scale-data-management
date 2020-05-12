from flask import Flask, jsonify, make_response
from http import HTTPStatus
from database.database import Database
from external_services import CouldNotSubtractCredit, \
    CouldNotRetrieveOrderCost, retrieve_order_cost, subtract_user_credit


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

    @service.route('/pay/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def complete_payment(user_id, order_id):
        try:
            order_cost = retrieve_order_cost(order_id)
            subtract_user_credit(user_id, order_cost)
            try:
                db.set_payment_status(order_id, "PAID")
            except:
                # If we cannot store the entry in the db, revert.
                # TODO: Figure out how te revert.
                pass
            return make_response(jsonify(), HTTPStatus.CREATED)
        except CouldNotRetrieveOrderCost as e:
            # If we cannot find the order_cost.
            # TODO: Determine correct HTTPStatus
            return make_response(jsonify({
                "error": "Could not find order"
            }), HTTPStatus.BAD_REQUEST)
        except CouldNotSubtractCredit as e:
            # If we cannot subtract the amount
            # TODO: Determine correct HTTPStatus
            return make_response(jsonify({
                "error": "Not enough credits on account"
            }), HTTPStatus.BAD_REQUEST)

    @service.route('/cancel/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def cancel_payment(user_id, order_id):
        db.set_payment_status(order_id, "CANCELLED")
        return make_response(jsonify(), HTTPStatus.CREATED)

    @service.route('/status/<uuid:order_id>', methods=["GET"])
    def get_order_status(order_id):
        order_status = db.get_payment_status(order_id)
        if order_status is not None:
            return make_response(jsonify({
                "order_id": order_id,
                "status": order_status
            }), HTTPStatus.OK)
        else:
            return make_response(jsonify(), HTTPStatus.NOT_FOUND)

    return service

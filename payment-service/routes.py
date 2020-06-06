from flask import Flask, jsonify, make_response
from http import HTTPStatus
from database.database import Database

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
        db.set_payment_status(order_id, "PAID")
        return make_response(jsonify(), HTTPStatus.CREATED)

    @service.route('/cancel/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def cancel_payment(user_id, order_id):
        db.set_payment_status(order_id, "CANCELLED")
        return make_response(jsonify(), HTTPStatus.CREATED)

    @service.route('/status/<uuid:order_id>', methods=["GET"])
    def get_order_status(order_id):
        order_status = db.get_payment_status(order_id)
        return make_response(jsonify({
            "order_id": order_id,
            "paid": order_status == "PAID"
        }), HTTPStatus.OK)

    return service


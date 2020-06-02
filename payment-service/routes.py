from flask import Flask
from http import HTTPStatus
from database.database import Database, DatabaseException
from external_services import CouldNotSubtractCredit, \
    CouldNotAddCredit, retrieve_order_cost, subtract_user_credit, \
    add_user_credit


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
        return {"status": "ok", "database": db.DATABASE}

    @service.route('/pay/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def complete_payment(user_id, order_id):
        order_cost = retrieve_order_cost(order_id)
        try:
            # This order was chosen as the possible rollback will be local
            # (within this service) instead of using external requests.
            db.set_payment_status(order_id, "PAID")
            subtract_user_credit(user_id, order_cost)
        except DatabaseException:
            # Failed to store the paid status.
            return {}, HTTPStatus.INTERNAL_SERVER_ERROR
        except CouldNotSubtractCredit:
            # Not enough credit.
            return {"error": "Not enough credit"}, HTTPStatus.BAD_REQUEST
        return {}, HTTPStatus.CREATED

    @service.route('/cancel/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def cancel_payment(user_id, order_id):
        order_status = db.get_payment_status(order_id)
        if order_status == "PAID":
            order_cost = retrieve_order_cost(order_id)
            try:
                # This order was chosen as the possible rollback will be local
                # (within this service) instead of using external requests.
                db.set_payment_status(order_id, "CANCELLED")
                add_user_credit(user_id, order_cost)
            except DatabaseException:
                # Failed to update the database status.
                return {}, HTTPStatus.INTERNAL_SERVER_ERROR
            except CouldNotAddCredit:
                # If we couldn't revert the credit, rollback the status update.
                db.set_payment_status(order_id, "PAID")
        elif order_status is None:
            db.set_payment_status(order_id, "CANCELLED")
            return 'success', HTTPStatus.CREATED
        else:
            return {}, HTTPStatus.BAD_REQUEST

    @service.route('/status/<uuid:order_id>', methods=["GET"])
    def get_order_status(order_id):
        order_status = db.get_payment_status(order_id)
        if order_status is not None:
            return {
                "paid": order_status == "PAID"
            }, HTTPStatus.OK
        else:
            return 'failure', HTTPStatus.NOT_FOUND

    return service

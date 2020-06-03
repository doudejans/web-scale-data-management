from flask import Flask
from http import HTTPStatus
from database.database import Database, DatabaseException
from external_services import CouldNotSubtractCredit, CouldNotAddCredit, \
    subtract_user_credit, add_user_credit


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

    @service.route('/pay/<uuid:user_id>/<uuid:order_id>/<int:amount>', methods=[
        "POST"])
    def complete_payment(user_id, order_id, amount):
        try:
            # This order was chosen as the possible rollback will be local
            # (within this service) instead of using external requests.
            db.insert_payment_status(order_id, "PAID", amount)
            subtract_user_credit(user_id, amount)
        except DatabaseException:
            # Failed to store the paid status.
            return 'failure', HTTPStatus.INTERNAL_SERVER_ERROR
        except CouldNotSubtractCredit:
            # Not enough credit.
            db.set_payment_status(order_id, "FAILED")
            return {"error": "Not enough credit"}, HTTPStatus.BAD_REQUEST
        return 'success', HTTPStatus.CREATED

    @service.route('/cancel/<uuid:user_id>/<uuid:order_id>', methods=["POST"])
    def cancel_payment(user_id, order_id):
        order_status, order_cost = db.get_payment(order_id)
        if order_status == "PAID":
            try:
                # This order was chosen as the possible rollback will be local
                # (within this service) instead of using external requests.
                db.set_payment_status(order_id, "REFUNDED")
                add_user_credit(user_id, order_cost)
                return 'success', HTTPStatus.OK
            except DatabaseException:
                # Failed to update the database status.
                return 'failure', HTTPStatus.INTERNAL_SERVER_ERROR
            except CouldNotAddCredit:
                # If we couldn't revert the credit, rollback the status update.
                db.set_payment_status(order_id, "PAID")
                return {"error": "Unable to return credit"}, HTTPStatus.BAD_REQUEST
        elif order_status is None:
            db.insert_payment_status(order_id, "CANCELLED", None)
            return 'success', HTTPStatus.CREATED
        else:
            return 'failure', HTTPStatus.BAD_REQUEST

    @service.route('/status/<uuid:order_id>', methods=["GET"])
    def get_order_status(order_id):
        order_status, _ = db.get_payment(order_id)
        return {
            "paid": order_status == "PAID"
        }, HTTPStatus.OK

    return service

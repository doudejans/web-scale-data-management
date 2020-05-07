from flask import Flask, jsonify
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

    # TODO: Add the microservice routes here...
    @service.route('/pay/:user_id/:order_id', methods=["POST"])
    def complete_payment():
        pass

    @service.route('/cancel/:user_id/:order_id', methods=["POST"])
    def cancel_payment():
        pass

    @service.route('/status/:order_id', methods=["GET"])
    def get_order_status():
        pass

    return service


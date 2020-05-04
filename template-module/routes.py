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

    # Define the route from the point where it is unique,
    # so '/users/create' ->
    # '/create'. The '/users' part will be handled by the proxy.
    @service.route('/create')
    def create_x():
        # I have implemented this example route using the example query
        # present in both the cassandra and postgres database.
        return jsonify({"version": db.retrieve_version()})

    # TODO: Add the microservice routes here...

    return service


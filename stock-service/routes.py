import uuid
from http import HTTPStatus

from flask import Flask, jsonify, make_response, request
from database.database import Database


# This is the main file of the service, handling with the different routes
# the microservice exposes.


# The db variable here can be either 'db_postgres.py' or 'db_cassandra.py'
# based on the config given to the application.
def create_app(db: Database):
    service = Flask(__name__)

    # The db variable will be set by app.py to either cassandra or postgres
    # depending on flags used when starting the application.

    @service.route('/health')
    def health():
        return jsonify({"status": "ok", "database": db.DATABASE})

    # Get stock item availability.
    @service.route('/find/<uuid:item_id>', methods=["GET"])
    def get_availability(item_id):
        res = db.find_stock(item_id)
        if res is not None:
            return make_response(jsonify({"stock": res[0], "price": res[1]}), HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # Subtract from existing stock.
    @service.route('/subtract/<uuid:item_id>/<int:number>', methods=["POST"])
    def stock_subtract(item_id, number):
        success = db.stock_subtract(item_id, number)
        if success:
            return make_response('success', HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # Add to existing stock.
    @service.route('/add/<uuid:item_id>/<int:number>', methods=["POST"])
    def stock_add(item_id, number):
        success = db.stock_add(item_id, number)
        if success:
            return make_response('success', HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # Create stock and return the ID.
    @service.route('/item/create/<int:price>', methods=["POST"])
    def create_stock(price):
        uuid = db.create_stock(price)
        if uuid is not None:
            return make_response(jsonify({"item_id": uuid}), HTTPStatus.OK)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    # Subtract a batch of items.
    @service.route('/batchSubtract', methods=["POST"])
    def batch_subtract():
        content = request.json
        if content is not None:
            items = map(lambda item: uuid.UUID(item), content["items"])
            success = db.batch_subtract(items)
            if success:
                return make_response('success', HTTPStatus.OK)
            else:
                return make_response('failure', HTTPStatus.BAD_REQUEST)
        else:
            return make_response('failure', HTTPStatus.BAD_REQUEST)

    return service

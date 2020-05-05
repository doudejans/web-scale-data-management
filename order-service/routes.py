from flask import Flask, jsonify
from database.database import Database
from uuid import uuid4, UUID


def create_app(db: Database):
    service = Flask(__name__)

    @service.route('/health')
    def health():
        return jsonify({"status": "ok", "database": db.DATABASE})

    @service.route('/create/<uuid:user_id>', methods=['POST'])
    def create_order(user_id: UUID):
        order_id = uuid4()
        db.add_order(order_id, user_id)
        return str(order_id)

    # TODO: Add the microservice routes here...

    return service


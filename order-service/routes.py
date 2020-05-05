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
        return jsonify({"status": 200, "order_id": str(order_id)})

    @service.route('/remove/<uuid:order_id>', methods=['DELETE'])
    def remove_order(order_id: UUID):
        db.remove_order(order_id)
        return jsonify({"status": 200, "message": "success"})

    return service


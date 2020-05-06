from flask import Flask, jsonify
from database.database import Database
from uuid import uuid4, UUID
from http import HTTPStatus


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
        db.delete_order(order_id)
        return jsonify({"status": 200, "message": "success"})

    @service.route('/find/<uuid:order_id>')
    def find_order(order_id: UUID):
        user_id = db.get_order(order_id)
        if user_id is None:
            return jsonify({"status": 404, "message": "Order not found"}), 404

        # TODO: add items for order and payment status

        return jsonify({"status": 200, "order": {"order_id": order_id, "user_id": user_id}})

    return service


from uuid import uuid4, UUID

from flask import Flask, jsonify

from database.database import Database


def create_app(db: Database):
    service = Flask(__name__)

    @service.route('/health')
    def health():
        return jsonify({"status": "ok", "database": db.DATABASE})

    @service.route('/create/<uuid:user_id>', methods=['POST'])
    def create_order(user_id: UUID):
        order_id = uuid4()
        db.add_order(order_id, user_id)
        return jsonify({'status': 201, 'order_id': str(order_id)}), 201

    @service.route('/remove/<uuid:order_id>', methods=['DELETE'])
    def remove_order(order_id: UUID):
        db.delete_order(order_id)
        return jsonify({'status': 200, 'message': 'success'})

    @service.route('/find/<uuid:order_id>')
    def find_order(order_id: UUID):
        order = db.get_order(order_id)
        if order is None:
            return jsonify({'status': 404, 'message': 'Order not found'}), 404

        # TODO: contact payment service for status

        return jsonify({'status': 200, 'order': order})

    @service.route('/addItem/<uuid:order_id>/<uuid:item_id>', methods=['POST'])
    def add_item_to_order(order_id: UUID, item_id: UUID):
        found_order = db.add_item_to_order(order_id, item_id)

        if found_order:
            return jsonify({'status': 200, 'message': 'success'})
        else:
            return jsonify({'status': 404, 'message': 'Order not found'}), 404

    @service.route('/removeItem/<uuid:order_id>/<uuid:item_id>', methods=['DELETE'])
    def remove_item_from_order(order_id: UUID, item_id: UUID):
        found_order = db.remove_item_from_order(order_id, item_id)

        if found_order:
            return jsonify({'status': 200, 'message': 'success'})
        else:
            return jsonify({'status': 404, 'message': 'Order not found'}), 404

    @service.route('/checkout/<uuid:order_id>', methods=['POST'])
    def checkout_order(order_id: UUID):
        # TODO: Contact stock service
        # TODO: Contact payment service
        return jsonify({'status': 200, 'message': 'Not implemented yet'})

    return service


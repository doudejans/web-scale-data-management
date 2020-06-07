from uuid import uuid4, UUID
from flask import Flask, jsonify

from database.database import Database
from external_services import get_payment_status, get_total_item_cost, initiate_payment, subtract_stock, \
    retract_payment, CouldNotRetractPayment, \
    CouldNotRetrievePaymentStatus, CouldNotRetrieveItemCost, CouldNotInitiatePayment, CouldNotSubtractStock


def create_app(db: Database):
    service = Flask(__name__)

    @service.route('/health')
    def health():
        return jsonify({"status": "ok", "database": db.DATABASE})

    @service.route('/create/<uuid:user_id>', methods=['POST'])
    def create_order(user_id: UUID):
        order_id = uuid4()
        db.add_order(order_id, user_id)
        return jsonify({'order_id': str(order_id)}), 201

    @service.route('/remove/<uuid:order_id>', methods=['DELETE'])
    def remove_order(order_id: UUID):
        db.delete_order(order_id)
        return jsonify({'message': 'success'})

    @service.route('/find/<uuid:order_id>')
    def find_order(order_id: UUID):
        order = db.get_order(order_id)
        if order is None:
            return jsonify({'message': 'Order not found'}), 404

        try:
            paid = get_payment_status(order_id)
            total_cost = get_total_item_cost(order['items'])
        except CouldNotRetrievePaymentStatus:
            return jsonify({'message': 'Could not retrieve payment status'}), 500
        except CouldNotRetrieveItemCost:
            return jsonify({'message': 'Could not retrieve order item cost'}), 500

        return jsonify({
            'paid': paid,
            'total_cost': total_cost,
            **order
        })

    @service.route('/addItem/<uuid:order_id>/<uuid:item_id>', methods=['POST'])
    def add_item_to_order(order_id: UUID, item_id: UUID):
        found_order = db.add_item_to_order(order_id, item_id)

        if found_order:
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': 'Order not found'}), 404

    @service.route('/removeItem/<uuid:order_id>/<uuid:item_id>', methods=['DELETE'])
    def remove_item_from_order(order_id: UUID, item_id: UUID):
        found_order = db.remove_item_from_order(order_id, item_id)

        if found_order:
            return jsonify({'message': 'success'})
        else:
            return jsonify({'message': 'Order not found'}), 404

    @service.route('/checkout/<uuid:order_id>', methods=['POST'])
    def checkout_order(order_id: UUID):
        order = db.get_order(order_id)

        try:
            total_cost = get_total_item_cost(order['items'])
            initiate_payment(order['user_id'], order_id, total_cost)
            subtract_stock(order['items'])

        except CouldNotRetrieveItemCost:
            return jsonify({'message': 'Could not retrieve order item cost'}), 500
        except CouldNotInitiatePayment:
            return jsonify({'message': 'Payment failed'}), 400
        except CouldNotSubtractStock:
            try:
                retract_payment(order['user_id'], order['order_id'])
                return jsonify({'message': 'Could not subtract stock'}), 400
            except CouldNotRetractPayment:
                return jsonify({'message': 'Checkout transaction failed'}), 500

        return jsonify({'message': 'success'})

    return service


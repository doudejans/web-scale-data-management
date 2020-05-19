from flask import Blueprint
import request

saga_listener = Blueprint('saga_listener', __name__)

# This subscriptions list is specific
subscriptions = {}


@saga_listener.route('/event/<event:str>/<transaction_id:str>')
def on_event(event, transaction_id):
    """Handle incoming events by event type and transaction id."""
    if event in subscriptions:
        for callback in subscriptions[event]:
            callback(transaction_id)


def subscribe_to(service: str, event: str, callback):
    """Subscribe to a service for a specific event."""
    request.post(f'{service}/subscribe/{event}')
    if event not in subscriptions:
        subscriptions[event] = []
    subscriptions[event].append(callback)

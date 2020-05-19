from flask import Blueprint
import requests

CALLBACK_URL = ""
saga_listener = Blueprint('saga_listener', __name__)
subscriptions = {}


@saga_listener.route('/event/<event:str>/<transaction_id:str>')
def on_event(event, transaction_id):
    """Handle incoming events by event type and transaction id."""
    if event in subscriptions:
        for callback in subscriptions[event]:
            callback(transaction_id)


def subscribe_to(service: str, event: str, callback):
    """Subscribe to a service for a specific event."""
    # In terms of replicas only one needs to call the subscribe function,
    # however as we should not communicate between replicas we call again.

    requests.post(f'{service}/subscribe/{event}',
                  json={"callback_url": CALLBACK_URL})
    if event not in subscriptions:
        subscriptions[event] = []
    subscriptions[event].append(callback)

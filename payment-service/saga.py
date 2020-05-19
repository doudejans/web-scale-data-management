from flask import Blueprint
from enum import Enum

saga = Blueprint('saga', __name__)


class Events(Enum):
    PAYMENT_FAILED = 0
    PAYMENT_INITATED = 1
    PAYMENT_RESERVED = 2


# For demonstration purposes the subscriptions list is stored locally. However
# when replicas are used (in deployment) the list should be stored somewhere
# externally such that each replica can access it.
# The list can be optimised for few writes, many reads.
# TODO: Move subscriptions list to external service.
subscriptions = {}
# Add all events to the subscription list as keys.
for event in Events:
    subscriptions[event] = set()


@saga.route('/subscribe/<event_name:string>')
def subscribe_to(event_name):
    event = __find_event_by_name(event_name)
    # TODO: Figure out how to send and receive callback url
    subscriptions[event].add("callback_url")
    pass


def __find_event_by_name(event_name):
    matches = [event for event in Events if event.name == event_name]
    if len(matches) == 0:
        return None
    else:
        return matches[0]

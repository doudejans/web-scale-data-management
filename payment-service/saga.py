from flask import Blueprint, make_response, request
from http import HTTPStatus
from enum import Enum
import requests

saga = Blueprint('saga', __name__)


class Events(Enum):
    PAYMENT_FAILED = 0
    PAYMENT_INITATED = 1
    PAYMENT_RESERVED = 2


# For demonstration purposes the subscriptions set is stored locally. However
# when replicas are used (in deployment) the set should be stored somewhere
# externally such that each replica can access it.
# The set can be optimised for few writes, many reads as we only need to add
# the subscription once.
# TODO: Move subscriptions set to external service.
subscriptions = {}
# Add all events to the subscription list as keys.
for event in Events:
    subscriptions[event] = set()


@saga.route('/subscribe/<event_name:string>')
def subscribe_to(event_name):
    data = request.get_json()
    event = __find_event_by_name(event_name)
    # TODO: Figure out how to send and receive callback url
    subscriptions[event].add(data["callback_url"])
    return make_response('success', HTTPStatus.OK)


def post_event(event: Events, transaction_id: str):
    """Let all subscribers of a given event know about the given transaction"""
    for subscriber in subscriptions[event]:
        requests.post(f"{subscriber}/event/{event.name}/{transaction_id}")


def __find_event_by_name(event_name):
    matches = [event for event in Events if event.name == event_name]
    if len(matches) == 0:
        return None
    else:
        return matches[0]

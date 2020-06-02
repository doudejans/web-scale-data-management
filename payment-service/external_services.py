import requests
import os
from http import HTTPStatus

USER_SERVICE_BASE = os.environ.get("USER_SERVICE", "http://localhost:5000/users")
ORDER_SERVICE_BASE = os.environ.get("ORDER_SERVICE", "http://localhost:5000/orders")


class CouldNotRetrieveOrderCost(Exception):
    pass


class CouldNotSubtractCredit(Exception):
    pass


class CouldNotAddCredit(Exception):
    pass


def retrieve_order_cost(order_id) -> float:
    """Retrieves the total cost of an order from the orders service."""
    resp = requests.get(f"{ORDER_SERVICE_BASE}/find/{order_id}")
    # TODO: Check status code.
    if resp.status_code == HTTPStatus.OK:
        # TODO: Check totalCost retrieval.
        return float(resp.json()['total_cost'])
    else:
        raise CouldNotRetrieveOrderCost()


def subtract_user_credit(user_id, amount):
    """Subtracts the user credit using the user service."""
    resp = requests.post(f"{USER_SERVICE_BASE}/credit/subtract/{user_id}/"
                         f"{amount}")
    if resp.status_code != HTTPStatus.OK:
        raise CouldNotSubtractCredit


def add_user_credit(user_id, amount):
    """Adds the user credit using the user service."""
    resp = requests.post(f"{USER_SERVICE_BASE}/credit/add/{user_id}/"
                         f"{amount}")
    if resp.status_code != HTTPStatus.OK:
        raise CouldNotAddCredit()
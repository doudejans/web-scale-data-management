import requests
from http import HTTPStatus

USER_SERVICE_BASE = "https://user-service"
ORDER_SERVICE_BASE = "https://order-service"


class CouldNotRetrieveOrderCost(Exception):
    pass


class CouldNotSubtractCredit(Exception):
    pass


def retrieve_order_cost(order_id) -> float:
    """Retrieves the total cost of an order from the orders service."""
    resp = requests.get(f"{ORDER_SERVICE_BASE}/totalCost/{order_id}")
    # TODO: Check status code.
    if resp.status_code == HTTPStatus.OK:
        # TODO: Check totalCost retrieval.
        return float(resp.json()['totalCost'])
    else:
        raise CouldNotRetrieveOrderCost()


def subtract_user_credit(user_id, amount):
    """Subtracts the user credit using the user service."""
    resp = requests.post(f"{USER_SERVICE_BASE}/credit/subtract/{user_id}/"
                         f"{amount}")
    if resp.status_code != HTTPStatus.OK:
        raise CouldNotSubtractCredit

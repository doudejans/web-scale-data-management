import os
import requests

PAYMENT_SERVICE_BASE = os.environ.get("PAYMENT_SERVICE", "http://localhost:8000/payment")
STOCK_SERVICE_BASE = os.environ.get("STOCK_SERVICE", "http://localhost:8000/stock")


class CouldNotRetrievePaymentStatus(Exception):
    pass


class CouldNotRetrieveItemCost(Exception):
    pass

class CouldNotInitiatePayment(Exception):
    pass


def get_payment_status(order_id):
    res = requests.get(f"{PAYMENT_SERVICE_BASE}/status/{order_id}")

    if res.ok:
        return res.json()['paid']
    else:
        raise CouldNotRetrievePaymentStatus()


def initiate_payment(user_id, order_id, amount):
    res = requests.get(f"{PAYMENT_SERVICE_BASE}/pay/{user_id}/{order_id}/{amount}")

    if not res.ok:
        raise CouldNotInitiatePayment()


def get_total_item_cost(items):
    try:
        total_cost = sum([__get_item_cost(item_id) for item_id in items])
    except CouldNotRetrieveItemCost:
        raise CouldNotRetrieveItemCost

    return total_cost


def __get_item_cost(item_id):
    res = requests.get(f"{STOCK_SERVICE_BASE}/find/{item_id}")

    if res.ok:
        return int(res.json()['price'])
    else:
        raise CouldNotRetrieveItemCost()
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


class CouldNotSubtractStock(Exception):
    pass


class CouldNotRetractPayment(Exception):
    pass


def get_payment_status(order_id):
    res = requests.get(f"{PAYMENT_SERVICE_BASE}/status/{order_id}")

    if res.ok:
        return res.json()['paid']
    else:
        raise CouldNotRetrievePaymentStatus()


def initiate_payment(user_id, order_id, amount):
    res = requests.post(f"{PAYMENT_SERVICE_BASE}/pay/{user_id}/{order_id}/{amount}")

    if not res.ok:
        raise CouldNotInitiatePayment()


def retract_payment(user_id, order_id):
    res = requests.post(f"{PAYMENT_SERVICE_BASE}/cancel/{user_id}/{order_id}")

    if not res.ok:
        raise CouldNotRetractPayment()


def subtract_stock(items):
    res = requests.post(f"{STOCK_SERVICE_BASE}/batchSubtract", json={
        'items': [str(item) for item in items]
    })

    if not res.ok:
        raise CouldNotSubtractStock()


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

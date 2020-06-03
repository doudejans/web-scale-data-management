import os
import requests

PAYMENT_SERVICE_BASE = os.environ.get("PAYMENT_SERVICE", "http://localhost:5000/payment")
STOCK_SERVICE_BASE = os.environ.get("STOCK_SERVICE_BASE", "http://localhost:5000/stock")


class CouldNotRetrievePaymentStatus(Exception):
    pass

def get_payment_status(order_id):
    res = requests.get(f"{PAYMENT_SERVICE_BASE}/status/{order_id}")

    if res.ok:
        return res.json()['paid']
    else:
        raise CouldNotRetrievePaymentStatus()
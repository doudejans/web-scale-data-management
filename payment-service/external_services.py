import requests
import os
from http import HTTPStatus

USER_SERVICE_BASE = os.environ.get("USER_SERVICE",
                                   "http://localhost:5000/users")


class CouldNotSubtractCredit(Exception):
    pass


class CouldNotAddCredit(Exception):
    pass


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

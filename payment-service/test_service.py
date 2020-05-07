import requests
from uuid import uuid4
from http import HTTPStatus

SERVICE_URL = "http://localhost:5000"

def __create_order():
    order_id = uuid4()
    user_id = uuid4()
    return order_id, user_id;

def __pay_order_request(order_id, user_id):
    return requests.post(f'{SERVICE_URL}/pay/{user_id}/{order_id}')

def __cancel_order_request(order_id, user_id):
    return requests.post(f'{SERVICE_URL}/cancel/{user_id}/{order_id}')

def __get_order_status_request(order_id):
    return requests.get(f'{SERVICE_URL}/status/{order_id}')

def test_complete_purchase():
    order_id, user_id = __create_order();
    pay_resp = __pay_order_request(order_id, user_id)
    assert pay_resp.status_code == HTTPStatus.CREATED

    status_resp = __get_order_status_request(order_id)
    assert status_resp.json()["status"] == "PAID"

def test_cancel_purchase():
    order_id, user_id = __create_order();
    response = __cancel_order_request(order_id, user_id)
    assert response.status_code == HTTPStatus.CREATED

    status_resp = __get_order_status_request(order_id)
    assert status_resp.json()["status"] == "CANCELLED"

def test_could_not_find():
    order_id, _ = __create_order()
    status_resp = __get_order_status_request(order_id)
    assert status_resp.status_code == HTTPStatus.NOT_FOUND

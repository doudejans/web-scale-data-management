import requests
from uuid import UUID
from http import HTTPStatus

SERVICE_URL = "http://localhost:5000"

def __create_user_request():
    return requests.post(f'{SERVICE_URL}/create')

def __remove_user_request(user_id):
    return requests.post(f'{SERVICE_URL}/remove/{user_id}')

def __get_credit_request(user_id):
    return requests.get(f'{SERVICE_URL}/credit/{user_id}')

def __credit_subtract_request(user_id, amount):
    return requests.get(f'{SERVICE_URL}/credit/subtract/{user_id}/{amount}')

def __credit_add_request(user_id, amount):
    return requests.get(f'{SERVICE_URL}/credit/add/{user_id}/{amount}')

def test_all():
    response = __create_user_request()
    assert response.status_code == HTTPStatus.CREATED
    user_id = UUID(response.text)
    assert __get_credit_request(user_id).text == '0'
    assert __credit_subtract_request(user_id, 0).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 1).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_add_request(user_id, 0).status_code == HTTPStatus.OK
    assert __credit_add_request(user_id, 1).status_code == HTTPStatus.OK
    assert __get_credit_request(user_id).text == '1'
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_subtract_request(user_id, 1).status_code == HTTPStatus.OK
    assert __get_credit_request(user_id).text == '0'
    assert __credit_add_request(user_id, 4).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.OK
    assert __get_credit_request(user_id).text == '0'
    assert __remove_user_request(user_id).status_code == HTTPStatus.OK
    assert __remove_user_request(user_id).status_code == HTTPStatus.BAD_REQUEST
    assert __get_credit_request(user_id).status_code == HTTPStatus.NOT_FOUND
    assert __get_credit_request(user_id).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_subtract_request(user_id, 0).status_code == HTTPStatus.BAD_REQUEST
    assert __create_user_request().text != __create_user_request().text
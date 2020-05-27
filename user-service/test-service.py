import json
from http import HTTPStatus
from uuid import UUID

import requests

SERVICE_URL = "http://localhost/users"


def __create_user_request():
    return requests.post(f'{SERVICE_URL}/create')


def __remove_user_request(user_id):
    return requests.delete(f'{SERVICE_URL}/remove/{user_id}')


def __find_user_request(user_id):
    return requests.get(f'{SERVICE_URL}/find/{user_id}')


def __credit_subtract_request(user_id, amount):
    return requests.post(f'{SERVICE_URL}/credit/subtract/{user_id}/{amount}')


def __credit_add_request(user_id, amount):
    return requests.post(f'{SERVICE_URL}/credit/add/{user_id}/{amount}')


def test_all():
    response = __create_user_request()
    assert response.status_code == HTTPStatus.CREATED
    user_id = UUID(json.loads(response.text)['id'])
    assert json.loads(__find_user_request(user_id).text)['credit'] == '0'
    assert __credit_subtract_request(user_id, 0).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 1).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_add_request(user_id, 0).status_code == HTTPStatus.OK
    assert __credit_add_request(user_id, 1).status_code == HTTPStatus.OK
    assert json.loads(__find_user_request(user_id).text)['credit'] == '1'
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_subtract_request(user_id, 1).status_code == HTTPStatus.OK
    assert json.loads(__find_user_request(user_id).text)['credit'] == '0'
    assert __credit_add_request(user_id, 4).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.OK
    assert __credit_subtract_request(user_id, 2).status_code == HTTPStatus.OK
    assert json.loads(__find_user_request(user_id).text)['credit'] == '0'
    assert __remove_user_request(user_id).status_code == HTTPStatus.OK
    assert __remove_user_request(user_id).status_code == HTTPStatus.BAD_REQUEST
    assert __find_user_request(user_id).status_code == HTTPStatus.NOT_FOUND
    assert __credit_add_request(user_id, 0).status_code == HTTPStatus.BAD_REQUEST
    assert __credit_subtract_request(user_id, 0).status_code == HTTPStatus.BAD_REQUEST
    assert __create_user_request().text != __create_user_request().text

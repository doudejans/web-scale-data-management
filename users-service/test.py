import requests
from http import HTTPStatus
import uuid

FAILURE = 500

response = requests.post(f'http://127.0.0.1:5000/create')
assert response.status_code == HTTPStatus.CREATED
user_id = uuid.UUID(response.text)
assert requests.get(f'http://127.0.0.1:5000/credit/{user_id}').text == '0'
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/0').status_code == HTTPStatus.OK
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/1').status_code == HTTPStatus.BAD_REQUEST
assert requests.post(f'http://127.0.0.1:5000/credit/add/{user_id}/0').status_code == HTTPStatus.OK
assert requests.post(f'http://127.0.0.1:5000/credit/add/{user_id}/1').status_code == HTTPStatus.OK
assert requests.get(f'http://127.0.0.1:5000/credit/{user_id}').text == '1'
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/2').status_code == HTTPStatus.BAD_REQUEST
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/1').status_code == HTTPStatus.OK
assert requests.get(f'http://127.0.0.1:5000/credit/{user_id}').text == '0'
assert requests.post(f'http://127.0.0.1:5000/credit/add/{user_id}/4').status_code == HTTPStatus.OK
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/2').status_code == HTTPStatus.OK
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/2').status_code == HTTPStatus.OK
assert requests.get(f'http://127.0.0.1:5000/credit/{user_id}').text == '0'
assert requests.delete(f'http://127.0.0.1:5000/remove/{user_id}').status_code == HTTPStatus.OK
assert requests.delete(f'http://127.0.0.1:5000/remove/{user_id}').status_code == HTTPStatus.BAD_REQUEST
assert requests.get(f'http://127.0.0.1:5000/credit/{user_id}').status_code == HTTPStatus.NOT_FOUND
assert requests.post(f'http://127.0.0.1:5000/credit/add/{user_id}/0').status_code == HTTPStatus.BAD_REQUEST
assert requests.post(f'http://127.0.0.1:5000/credit/subtract/{user_id}/0').status_code == HTTPStatus.BAD_REQUEST
assert requests.post(f'http://127.0.0.1:5000/create').text != requests.post(f'http://127.0.0.1:5000/create').text

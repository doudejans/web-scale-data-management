import requests


def test_create_user():
    response = requests.post("http://127.0.0.1:5000/create")
    assert response.status_code == 201


test_create_user()

import pytest

BASE_URL = "/api/v2/auth/login/"


@pytest.mark.django_db
def test_login_wrong_user(api_client):
    response = api_client.post(
        BASE_URL,
        {
            "email": "nonexistent@example.com",
            "password": "<PASSWORD>",
        },
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_login_bad_request(api_client):
    response = api_client.post(BASE_URL, {})
    assert response.status_code == 400


@pytest.mark.django_db
def test_login_ok(api_client, super_user, password):
    response = api_client.post(
        BASE_URL,
        {
            "email": super_user.email,
            "password": password,
        },
    )
    assert response.status_code == 200
    assert response.data == {}

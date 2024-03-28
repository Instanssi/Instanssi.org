import pytest

BASE_URL = "/api/v2/auth/logout/"


@pytest.mark.django_db
def test_logout_not_authenticated(api_client):
    response = api_client.post(BASE_URL)
    assert response.status_code == 401


@pytest.mark.django_db
def test_logout_bad_request(auth_client):
    response = auth_client.post(BASE_URL)
    assert response.status_code == 204

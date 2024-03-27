import pytest

BASE_URL = "/api/v2/auth/social_urls/"


@pytest.mark.django_db
def test_social_urls(api_client):
    response = api_client.get(BASE_URL)
    assert response.status_code == 200
    assert response.data == [
        {"method": "google", "url": "/login/google/?next=/users/login/", "name": "Google"},
        {"method": "github", "url": "/login/github/?next=/users/login/", "name": "Github"},
        {"method": "steam", "url": "/login/steam/?next=/users/login/", "name": "Steam"},
    ]

import pytest

BASE_URL = "/api/v2/auth/social_urls/"


@pytest.mark.django_db
def test_social_urls(api_client):
    response = api_client.get(BASE_URL)
    assert response.status_code == 200
    assert response.data == [
        {
            "method": "google",
            "url": "/accounts/google/login/?process=login&next=/accounts/login/",
            "name": "Google",
        },
        {
            "method": "github",
            "url": "/accounts/github/login/?process=login&next=/accounts/login/",
            "name": "Github",
        },
    ]

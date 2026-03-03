from urllib.parse import parse_qs, urlparse

import pytest
from django.urls import reverse

BASE_URL = "/api/v2/auth/social_urls/"


@pytest.mark.django_db
def test_social_urls(api_client):
    response = api_client.get(BASE_URL)
    assert response.status_code == 200
    login_url = reverse("account_login")
    methods = {item["method"] for item in response.data}
    assert "openid" not in methods
    assert "google" in methods
    assert "github" in methods
    assert "steam" in methods
    # All entries should have the expected structure and default next parameter
    for item in response.data:
        assert set(item.keys()) == {"method", "url", "name"}
        parsed = urlparse(item["url"])
        assert parse_qs(parsed.query)["next"] == [login_url]
    # Results should be sorted alphabetically by name
    names = [item["name"] for item in response.data]
    assert names == sorted(names)

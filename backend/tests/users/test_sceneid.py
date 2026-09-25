from urllib.parse import parse_qs, urlparse

import pytest
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

AUTHORIZE_URL = "https://id.scene.org/oauth/authorize/"
TOKEN_URL = "https://id.scene.org/oauth/token/"
PROFILE_URL = "https://id.scene.org/api/3.0/me/"

User = get_user_model()

SCENEID_USER = {
    "id": "1234",
    "first_name": "John",
    "last_name": "Doe",
    "display_name": "JohnD",
    "email": "john.doe@example.com",
}


def begin_login(client: Client) -> str:
    """Start the SceneID login flow and return the OAuth2 state parameter."""
    response = client.post(reverse("sceneid_login"))
    assert response.status_code == 302
    query = parse_qs(urlparse(response["Location"]).query)
    return query["state"][0]


@pytest.mark.django_db
def test_sceneid_login_redirects_to_authorize_url(client):
    response = client.post(reverse("sceneid_login"))

    assert response.status_code == 302
    location = response["Location"]
    assert location.startswith(AUTHORIZE_URL)
    query = parse_qs(urlparse(location).query)
    assert query["client_id"] == ["test-sceneid-id"]
    assert query["response_type"] == ["code"]
    assert set(query["scope"][0].split(" ")) == {"basic", "user:email"}
    assert query["state"]
    assert query["redirect_uri"][0].endswith("/users/sceneid/login/callback/")


@pytest.mark.django_db
def test_sceneid_callback_creates_user(client, requests_mock):
    state = begin_login(client)
    requests_mock.post(
        TOKEN_URL,
        json={
            "access_token": "test-access-token",
            "expires_in": "3600",
            "token_type": "Bearer",
            "scope": "basic user:email",
        },
        headers={"Content-Type": "application/json"},
    )
    requests_mock.get(PROFILE_URL, json={"success": True, "user": SCENEID_USER})

    response = client.get(reverse("sceneid_callback"), {"code": "test-code", "state": state})

    assert response.status_code == 302
    user = User.objects.get(email="john.doe@example.com")
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    account = SocialAccount.objects.get(user=user, provider="sceneid")
    assert account.uid == "1234"
    assert account.extra_data["display_name"] == "JohnD"
    email = EmailAddress.objects.get(user=user, email="john.doe@example.com")
    assert email.verified


@pytest.mark.django_db
def test_sceneid_token_request_uses_basic_auth(client, requests_mock):
    state = begin_login(client)
    requests_mock.post(
        TOKEN_URL,
        json={"access_token": "test-access-token"},
        headers={"Content-Type": "application/json"},
    )
    requests_mock.get(PROFILE_URL, json={"success": True, "user": SCENEID_USER})

    client.get(reverse("sceneid_callback"), {"code": "test-code", "state": state})

    token_requests = [r for r in requests_mock.request_history if r.url.startswith(TOKEN_URL)]
    assert len(token_requests) == 1
    assert token_requests[0].headers["Authorization"].startswith("Basic ")
    body = parse_qs(token_requests[0].text)
    assert body["grant_type"] == ["authorization_code"]
    assert body["code"] == ["test-code"]
    # Client credentials go into the basic auth header, not the body
    assert "client_id" not in body
    assert "client_secret" not in body


@pytest.mark.django_db
def test_sceneid_login_connects_to_existing_user_by_email(client, requests_mock):
    user = User.objects.create_user("existing", email="john.doe@example.com", password="hunter2")
    EmailAddress.objects.create(user=user, email="john.doe@example.com", verified=True, primary=True)
    state = begin_login(client)
    requests_mock.post(
        TOKEN_URL,
        json={"access_token": "test-access-token"},
        headers={"Content-Type": "application/json"},
    )
    requests_mock.get(PROFILE_URL, json={"success": True, "user": SCENEID_USER})

    user_count = User.objects.count()

    response = client.get(reverse("sceneid_callback"), {"code": "test-code", "state": state})

    assert response.status_code == 302
    assert User.objects.count() == user_count
    account = SocialAccount.objects.get(provider="sceneid", uid="1234")
    assert account.user == user


@pytest.mark.django_db
def test_sceneid_callback_handles_profile_error(client, requests_mock):
    state = begin_login(client)
    requests_mock.post(
        TOKEN_URL,
        json={"access_token": "test-access-token"},
        headers={"Content-Type": "application/json"},
    )
    requests_mock.get(PROFILE_URL, status_code=401, json={"success": False})

    response = client.get(reverse("sceneid_callback"), {"code": "test-code", "state": state})

    assert response.status_code == 401
    assert "socialaccount/authentication_error.html" in [t.name for t in response.templates]
    assert not User.objects.filter(email="john.doe@example.com").exists()
    assert not SocialAccount.objects.exists()


@pytest.mark.django_db
def test_sceneid_callback_handles_unsuccessful_profile_payload(client, requests_mock):
    state = begin_login(client)
    requests_mock.post(
        TOKEN_URL,
        json={"access_token": "test-access-token"},
        headers={"Content-Type": "application/json"},
    )
    requests_mock.get(PROFILE_URL, json={"success": False})

    response = client.get(reverse("sceneid_callback"), {"code": "test-code", "state": state})

    assert response.status_code == 401
    assert "socialaccount/authentication_error.html" in [t.name for t in response.templates]
    assert not User.objects.filter(email="john.doe@example.com").exists()
    assert not SocialAccount.objects.exists()

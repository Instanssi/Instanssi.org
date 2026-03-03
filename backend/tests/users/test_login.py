import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page(client):
    response = client.get(reverse("account_login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_with_credentials(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 302  # Redirect on successful login


@pytest.mark.django_db
def test_login_redirects_to_next(client, user):
    url = reverse("account_login") + "?next=/kompomaatti/"
    response = client.post(url, {"login": "testuser", "password": "testpass123"})
    assert response.status_code == 302
    assert response.url == "/kompomaatti/"


@pytest.mark.django_db
def test_login_redirects_to_profile_by_default(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 302
    assert response.url == reverse("users:profile")


@pytest.mark.django_db
def test_login_with_bad_credentials(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 200  # Re-renders form with errors


@pytest.mark.django_db
def test_logout_page(auth_client):
    response = auth_client.get(reverse("account_logout"))
    assert response.status_code == 302  # ACCOUNT_LOGOUT_ON_GET=True redirects


@pytest.mark.django_db
def test_loggedout_page(client):
    response = client.get(reverse("users:loggedout"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_account_inactive_page(client):
    response = client.get(reverse("account_inactive"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_social_login_cancelled_page(client):
    response = client.get(reverse("socialaccount_login_cancelled"))
    assert response.status_code == 200

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_login_page(client):
    response = client.get(reverse("account_login"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_ok(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "testuser", "password": "testpass123"},
    )
    assert response.status_code == 302


@pytest.mark.django_db
def test_login_wrong_credentials(client, user):
    response = client.post(
        reverse("account_login"),
        {"login": "testuser", "password": "wrongpassword"},
    )
    assert response.status_code == 200  # Re-renders form with errors

import pytest
from django.core import mail
from django.urls import reverse


@pytest.mark.django_db
def test_password_reset_page(client):
    response = client.get(reverse("account_reset_password"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_password_reset_request(client, user):
    response = client.post(
        reverse("account_reset_password"),
        {"email": "test@example.com"},
    )
    assert response.status_code == 302
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["test@example.com"]


@pytest.mark.django_db
def test_password_reset_unknown_email(client):
    response = client.post(
        reverse("account_reset_password"),
        {"email": "unknown@example.com"},
    )
    # Allauth redirects regardless to prevent email enumeration
    assert response.status_code == 302


@pytest.mark.django_db
def test_change_password_page(auth_client):
    response = auth_client.get(reverse("account_change_password"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_change_password(auth_client, user):
    response = auth_client.post(
        reverse("account_change_password"),
        {
            "oldpassword": "testpass123",
            "password1": "N3wP@ssw0rd!",
            "password2": "N3wP@ssw0rd!",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.check_password("N3wP@ssw0rd!")


@pytest.mark.django_db
def test_change_password_wrong_old_password(auth_client, user):
    response = auth_client.post(
        reverse("account_change_password"),
        {
            "oldpassword": "wrongpassword",
            "password1": "N3wP@ssw0rd!",
            "password2": "N3wP@ssw0rd!",
        },
    )
    assert response.status_code == 200  # Re-renders form with errors
    user.refresh_from_db()
    assert user.check_password("testpass123")  # Password unchanged


@pytest.mark.django_db
def test_change_password_redirects_unauthenticated(client):
    response = client.post(
        reverse("account_change_password"),
        {
            "oldpassword": "testpass123",
            "password1": "N3wP@ssw0rd!",
            "password2": "N3wP@ssw0rd!",
        },
    )
    assert response.status_code == 302
    assert "/users/login/" in response.url

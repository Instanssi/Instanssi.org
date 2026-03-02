import re

import pytest
from allauth.account.models import EmailAddress
from django.core import mail
from django.test import override_settings
from django.urls import reverse

from Instanssi.users.models import User


@pytest.mark.django_db
def test_signup_page(client):
    response = client.get(reverse("account_signup"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_with_valid_data(client):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_signup_with_mismatched_passwords(client):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "DifferentPassword!",
        },
    )
    assert response.status_code == 200  # Re-renders form with errors
    assert not User.objects.filter(username="newuser").exists()


@pytest.mark.django_db
def test_signup_with_duplicate_username(client, user):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "testuser",
            "email": "other@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
        },
    )
    assert response.status_code == 200  # Re-renders form with errors


@pytest.mark.django_db
def test_signup_with_optional_fields(client):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
            "first_name": "Test",
            "last_name": "User",
            "language": "fi",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username="newuser")
    assert user.first_name == "Test"
    assert user.last_name == "User"
    assert user.language == "fi"


@pytest.mark.django_db
def test_signup_without_optional_fields(client):
    response = client.post(
        reverse("account_signup"),
        {
            "username": "newuser",
            "email": "newuser@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
        },
    )
    assert response.status_code == 302
    user = User.objects.get(username="newuser")
    assert user.first_name == ""
    assert user.last_name == ""
    assert user.language == ""
    assert user.otherinfo == ""


@pytest.mark.django_db
@override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
def test_signup_email_verification_flow(client):
    """End-to-end: signup -> verification email -> confirm -> email verified."""
    # Sign up
    response = client.post(
        reverse("account_signup"),
        {
            "username": "verifyuser",
            "email": "verify@example.com",
            "password1": "T3stP@ssw0rd!",
            "password2": "T3stP@ssw0rd!",
        },
    )
    assert response.status_code == 302
    assert User.objects.filter(username="verifyuser").exists()
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["verify@example.com"]

    # Email should be unverified
    email_address = EmailAddress.objects.get(email="verify@example.com")
    assert not email_address.verified

    # Extract confirmation URL from the email body
    match = re.search(r"https?://\S+confirm-email/[^\s/]+/", mail.outbox[0].body)
    assert match, f"No confirmation URL found in email body: {mail.outbox[0].body}"
    confirm_url = match.group()
    # Strip the domain to get the path for the test client
    confirm_path = "/" + confirm_url.split("/", 3)[-1]

    # Visit the confirmation page
    response = client.get(confirm_path)
    assert response.status_code == 200

    # Confirm the email
    response = client.post(confirm_path)
    assert response.status_code == 302

    # Email should now be verified
    email_address.refresh_from_db()
    assert email_address.verified

import pytest
from allauth.account.models import EmailAddress
from django.test import override_settings

BASE_URL = "/api/v2/auth/login/"


@pytest.mark.django_db
def test_login_wrong_user(api_client):
    response = api_client.post(
        BASE_URL,
        {
            "username": "test",
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
            "username": super_user.username,
            "password": password,
        },
    )
    assert response.status_code == 200
    assert response.data == {}


@pytest.mark.django_db
@override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
def test_login_blocked_when_email_not_verified(api_client, base_user, password):
    response = api_client.post(
        BASE_URL,
        {
            "username": base_user.username,
            "password": password,
        },
    )
    assert response.status_code == 401
    assert response.data == {"code": "email_not_verified"}


@pytest.mark.django_db
@override_settings(ACCOUNT_EMAIL_VERIFICATION="mandatory")
def test_login_ok_when_email_verified(api_client, base_user, password):
    EmailAddress.objects.create(user=base_user, email=base_user.email, verified=True, primary=True)
    response = api_client.post(
        BASE_URL,
        {
            "username": base_user.username,
            "password": password,
        },
    )
    assert response.status_code == 200

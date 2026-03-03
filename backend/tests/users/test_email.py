import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse


@pytest.mark.django_db
def test_email_management_page(auth_client):
    response = auth_client.get(reverse("account_email"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_email_management_redirects_unauthenticated(client):
    response = client.get(reverse("account_email"))
    assert response.status_code == 302


@pytest.mark.django_db
def test_add_email(auth_client, user):
    response = auth_client.post(
        reverse("account_email"),
        {"email": "second@example.com", "action_add": ""},
    )
    assert response.status_code == 302
    assert EmailAddress.objects.filter(user=user, email="second@example.com").exists()


@pytest.mark.django_db
def test_add_duplicate_email(auth_client, user):
    response = auth_client.post(
        reverse("account_email"),
        {"email": "test@example.com", "action_add": ""},
    )
    assert response.status_code == 200  # Re-renders form with errors
    assert EmailAddress.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_add_email_redirects_unauthenticated(client):
    response = client.post(
        reverse("account_email"),
        {"email": "new@example.com", "action_add": ""},
    )
    assert response.status_code == 302
    assert "/users/login/" in response.url


@pytest.mark.django_db
def test_remove_email(auth_client, user):
    EmailAddress.objects.create(user=user, email="second@example.com", verified=True, primary=False)
    response = auth_client.post(
        reverse("account_email"),
        {"email": "second@example.com", "action_remove": ""},
    )
    assert response.status_code == 302
    assert not EmailAddress.objects.filter(email="second@example.com").exists()


@pytest.mark.django_db
def test_make_email_primary(auth_client, user):
    EmailAddress.objects.create(user=user, email="second@example.com", verified=True, primary=False)
    response = auth_client.post(
        reverse("account_email"),
        {"email": "second@example.com", "action_primary": ""},
    )
    assert response.status_code == 302
    assert EmailAddress.objects.get(email="second@example.com").primary


@pytest.mark.django_db
def test_cannot_remove_last_verified_email(auth_client, user):
    """Users must always keep at least one verified email address."""
    response = auth_client.post(
        reverse("account_email"),
        {"email": "test@example.com", "action_remove": ""},
    )
    assert response.status_code == 302
    assert EmailAddress.objects.filter(user=user, email="test@example.com", verified=True).exists()


@pytest.mark.django_db
def test_can_remove_unverified_email(auth_client, user):
    """Unverified emails can always be removed."""
    EmailAddress.objects.create(user=user, email="unverified@example.com", verified=False, primary=False)
    response = auth_client.post(
        reverse("account_email"),
        {"email": "unverified@example.com", "action_remove": ""},
    )
    assert response.status_code == 302
    assert not EmailAddress.objects.filter(email="unverified@example.com").exists()


@pytest.mark.django_db
def test_can_remove_verified_email_when_another_verified_exists(auth_client, user):
    """A verified email can be removed if another verified email remains."""
    EmailAddress.objects.create(user=user, email="second@example.com", verified=True, primary=False)
    response = auth_client.post(
        reverse("account_email"),
        {"email": "second@example.com", "action_remove": ""},
    )
    assert response.status_code == 302
    assert not EmailAddress.objects.filter(email="second@example.com").exists()
    assert EmailAddress.objects.filter(user=user, email="test@example.com", verified=True).exists()

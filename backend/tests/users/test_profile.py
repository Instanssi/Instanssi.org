import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_profile_redirects_unauthenticated(client):
    response = client.get(reverse("users:profile"))
    assert response.status_code == 302
    assert "/users/login/" in response.url


@pytest.mark.django_db
def test_profile_accessible_when_authenticated(auth_client):
    response = auth_client.get(reverse("users:profile"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_profile_update(auth_client, user):
    response = auth_client.post(
        reverse("users:profile"),
        {
            "first_name": "Updated",
            "last_name": "Name",
            "language": "fi",
            "otherinfo": "IRC: test",
        },
    )
    assert response.status_code == 302
    user.refresh_from_db()
    assert user.first_name == "Updated"
    assert user.last_name == "Name"
    assert user.language == "fi"
    assert user.otherinfo == "IRC: test"


@pytest.mark.django_db
def test_profile_update_does_not_change_email(auth_client, user):
    """Email cannot be changed via the profile form; it must go through allauth."""
    original_email = user.email
    auth_client.post(
        reverse("users:profile"),
        {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "sneaky@example.com",
            "language": "",
            "otherinfo": "",
        },
    )
    user.refresh_from_db()
    assert user.email == original_email

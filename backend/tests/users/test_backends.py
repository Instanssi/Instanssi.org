import pytest
from django.contrib.auth import authenticate

from Instanssi.users.models import User


@pytest.mark.django_db
def test_system_user_cannot_authenticate():
    User.objects.create_user(
        username="systembot", email="system@test.com", password="testpass123", is_system=True
    )
    assert authenticate(email="system@test.com", password="testpass123") is None


@pytest.mark.django_db
def test_normal_user_can_authenticate():
    user = User.objects.create_user(
        username="normaluser", email="normal@test.com", password="testpass123", is_system=False
    )
    assert authenticate(email="normal@test.com", password="testpass123") == user


@pytest.mark.django_db
def test_inactive_user_cannot_authenticate():
    User.objects.create_user(
        username="inactiveuser",
        email="inactive@test.com",
        password="testpass123",
        is_active=False,
        is_system=False,
    )
    assert authenticate(email="inactive@test.com", password="testpass123") is None

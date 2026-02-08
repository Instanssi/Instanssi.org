import pytest
from django.contrib.auth import authenticate

from Instanssi.users.models import User


@pytest.mark.django_db
def test_system_user_cannot_authenticate():
    user = User.objects.create_user(username="systembot", password="testpass123", is_system=True)
    assert authenticate(username="systembot", password="testpass123") is None


@pytest.mark.django_db
def test_normal_user_can_authenticate():
    user = User.objects.create_user(username="normaluser", password="testpass123", is_system=False)
    assert authenticate(username="normaluser", password="testpass123") == user


@pytest.mark.django_db
def test_inactive_user_cannot_authenticate():
    user = User.objects.create_user(
        username="inactiveuser", password="testpass123", is_active=False, is_system=False
    )
    assert authenticate(username="inactiveuser", password="testpass123") is None

import pytest
from django.contrib.auth import authenticate
from rest_framework import status

pytestmark = pytest.mark.django_db


def test_system_user_blocked_from_headless_login(headless_client, system_user):
    """Test that system users cannot login via the headless API."""
    response = headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": system_user.email, "password": "password"},
        format="json",
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_normal_user_can_headless_login(headless_client, base_user, password):
    """Test that normal users can login via the headless API."""
    response = headless_client.post(
        "/api/v2/allauth/browser/v1/auth/login",
        {"email": base_user.email, "password": password},
        format="json",
    )
    assert response.status_code == status.HTTP_200_OK


def test_system_user_blocked_at_backend_level(system_user, password):
    """Test that SystemUserAwareAuthBackend blocks system users from authenticate()."""
    result = authenticate(email=system_user.email, password=password)
    assert result is None


def test_normal_user_passes_backend_authenticate(base_user, password):
    """Test that normal users can authenticate via the backend."""
    result = authenticate(email=base_user.email, password=password)
    assert result == base_user

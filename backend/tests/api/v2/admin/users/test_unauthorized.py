"""Tests for unauthorized access to staff users endpoint."""

import pytest

BASE_URL = "/api/v2/admin/users/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_users_list(auth_client, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    assert auth_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("PUT", 403),
        ("PATCH", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_users_detail(auth_client, base_user, method, status):
    """Test unauthorized access to detail endpoint (Logged in, but no permissions)."""
    url = f"{BASE_URL}{base_user.id}/"
    assert auth_client.generic(method, url).status_code == status

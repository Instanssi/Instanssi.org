"""Tests for unauthorized access to staff events endpoint."""

import pytest

BASE_URL = "/api/v2/admin/events/"


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
def test_unauthorized_events_list(auth_client, method, status):
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
def test_unauthorized_events_detail(auth_client, event, method, status):
    """Test unauthorized access to detail endpoint (Logged in, but no permissions)."""
    url = f"{BASE_URL}{event.id}/"
    assert auth_client.generic(method, url).status_code == status

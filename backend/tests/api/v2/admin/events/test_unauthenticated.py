"""Tests for unauthenticated access to staff events endpoint."""

import pytest

BASE_URL = "/api/v2/admin/events/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_events_list(api_client, method, status):
    """Test unauthenticated access to list endpoint."""
    assert api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("PUT", 401),
        ("PATCH", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_events_detail(api_client, event, method, status):
    """Test unauthenticated access to detail endpoint."""
    url = f"{BASE_URL}{event.id}/"
    assert api_client.generic(method, url).status_code == status

"""Tests for unauthorized access to tokens endpoint."""

import pytest

BASE_URL = "/api/v2/tokens/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_tokens_list(auth_client, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    assert auth_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
    ],
)
def test_unauthorized_tokens_create(auth_client, method, status):
    """Test unauthorized access to create endpoint (Logged in, but no permissions)."""
    url = f"{BASE_URL}create/"
    assert auth_client.generic(method, url).status_code == status

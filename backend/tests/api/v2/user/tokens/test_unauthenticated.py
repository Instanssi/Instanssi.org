"""Tests for unauthenticated access to tokens endpoint."""

import pytest

BASE_URL = "/api/v2/tokens/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_tokens_list(api_client, method, status):
    """Test unauthenticated access to list endpoint."""
    assert api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_tokens_create(api_client, method, status):
    """Test unauthenticated access to create endpoint."""
    url = f"{BASE_URL}create/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("DELETE", 401),
    ],
)
def test_unauthenticated_tokens_detail(api_client, method, status):
    """Test unauthenticated access to detail endpoint."""
    url = f"{BASE_URL}12345/"
    assert api_client.generic(method, url).status_code == status

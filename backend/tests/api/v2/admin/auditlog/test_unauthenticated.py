"""Tests for unauthenticated access to audit log endpoint."""

import pytest

BASE_URL = "/api/v2/admin/auditlog/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
    ],
)
def test_unauthenticated_auditlog_list(api_client, method, status):
    """Test unauthenticated access to list endpoint."""
    assert api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
def test_unauthenticated_auditlog_detail(api_client):
    """Test unauthenticated access to detail endpoint."""
    url = f"{BASE_URL}1/"
    assert api_client.get(url).status_code == 401

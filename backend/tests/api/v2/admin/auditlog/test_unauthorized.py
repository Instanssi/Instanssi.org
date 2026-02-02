"""Tests for unauthorized access to audit log endpoint."""

import pytest

BASE_URL = "/api/v2/admin/auditlog/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
    ],
)
def test_unauthorized_auditlog_list(auth_client, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    assert auth_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
def test_unauthorized_auditlog_detail(auth_client):
    """Test unauthorized access to detail endpoint (Logged in, but no permissions)."""
    url = f"{BASE_URL}1/"
    assert auth_client.get(url).status_code == 403

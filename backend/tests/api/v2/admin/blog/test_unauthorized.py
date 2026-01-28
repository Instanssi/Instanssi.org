import pytest

BASE_URL = "/api/v2/admin/blog/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
        ("PATCH", 403),
        ("PUT", 403),
    ],
)
def test_unauthorized_list_denied(auth_client, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    assert auth_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
        ("PATCH", 403),
        ("PUT", 403),
    ],
)
def test_unauthorized_detail_denied(auth_client, public_blog_entry, method, status):
    """Test unauthorized access to detail endpoint (Logged in, but no permissions)."""
    url = f"{BASE_URL}{public_blog_entry.id}/"
    assert auth_client.generic(method, url).status_code == status

import pytest

BASE_URL = "/api/v2/admin/blog/"


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
def test_unauthenticated_blog_entries_list(api_client, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
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
def test_unauthenticated_blog_entries_detail(api_client, public_blog_entry, method, status):
    """Test unauthenticated access to detail endpoint (Not logged in)."""
    url = f"{BASE_URL}{public_blog_entry.id}/"
    assert api_client.generic(method, url).status_code == status

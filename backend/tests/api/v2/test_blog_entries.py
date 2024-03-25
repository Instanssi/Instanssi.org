import pytest

BASE_URL = "/api/v2/blog_entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 401),
        (True, "GET", 401),
        (False, "POST", 401),
        (True, "DELETE", 401),
        (True, "PATCH", 401),
        (True, "PUT", 401),
    ],
)
def test_unauthenticated_blog_entries(api_client, obj, method, status):
    """Test unauthenticated access (Not logged in)"""
    url = f"{BASE_URL}1/" if obj else BASE_URL
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "obj,method,status",
    [
        (False, "GET", 403),
        (True, "GET", 403),
        (False, "POST", 403),
        (True, "DELETE", 403),
        (True, "PATCH", 403),
        (True, "PUT", 403),
    ],
)
def test_unauthorized_blog_entries(user_api_client, obj, method, status):
    """Test unauthorized access (Logged in, but no permissions)"""
    url = f"{BASE_URL}1/" if obj else BASE_URL
    assert user_api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),
        ("POST", 400),
        ("DELETE", 405),
        ("PATCH", 405),
        ("PUT", 405),
    ],
)
def test_authorized_blog_entriesg(super_api_client, method, status):
    assert super_api_client.generic(method, BASE_URL).status_code == status

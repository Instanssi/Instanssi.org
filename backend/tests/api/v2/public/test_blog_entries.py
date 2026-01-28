import pytest
from django.conf import settings

BASE_URL = "/api/v2/public/blog_entries/"


@pytest.mark.django_db
def test_anonymous_can_list_public_entries(api_client, public_blog_entry, blog_entry):
    """Test that anonymous users can list public blog entries only."""
    req = api_client.get(BASE_URL)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": public_blog_entry.id,
            "date": public_blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
            "title": "Public test post",
            "text": "This is a public test blog entry.",
            "event": public_blog_entry.event_id,
        }
    ]


@pytest.mark.django_db
def test_anonymous_can_read_public_entry_detail(api_client, public_blog_entry):
    """Test that anonymous users can read a public blog entry detail."""
    req = api_client.get(f"{BASE_URL}{public_blog_entry.id}/")
    assert req.status_code == 200
    assert req.data["id"] == public_blog_entry.id
    assert req.data["title"] == "Public test post"


@pytest.mark.django_db
def test_anonymous_cannot_see_non_public_entries(api_client, blog_entry):
    """Test that non-public blog entries are not visible."""
    req = api_client.get(f"{BASE_URL}{blog_entry.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_anonymous_cannot_modify_blog_entries(api_client, public_blog_entry, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    url = f"{BASE_URL}{public_blog_entry.id}/"
    assert api_client.generic(method, url).status_code == status

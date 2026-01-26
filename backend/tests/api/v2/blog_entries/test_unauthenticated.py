import pytest
from django.conf import settings

BASE_URL = "/api/v2/blog_entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 401),
        ("DELETE", 401),
        ("PATCH", 401),
        ("PUT", 401),
    ],
)
def test_unauthenticated_write_denied(api_client, public_blog_entry, method, status):
    """Test unauthenticated write access is denied"""
    url = f"{BASE_URL}{public_blog_entry.id}/" if method != "POST" else BASE_URL
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthenticated_can_read_public_entries_list(api_client, public_blog_entry, blog_entry):
    """Test unauthenticated users can read public blog entries list"""
    result = api_client.get(BASE_URL)
    assert result.status_code == 200
    assert result.data == [
        {
            "id": public_blog_entry.id,
            "date": public_blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
            "title": "Public test post",
            "text": "This is a public test blog entry.",
            "event": public_blog_entry.event_id,
        }
    ]


@pytest.mark.django_db
def test_unauthenticated_can_read_public_entry_detail(api_client, public_blog_entry):
    """Test unauthenticated users can read a public blog entry"""
    result = api_client.get(f"{BASE_URL}{public_blog_entry.id}/")
    assert result.status_code == 200
    assert result.data == {
        "id": public_blog_entry.id,
        "date": public_blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "Public test post",
        "text": "This is a public test blog entry.",
        "event": public_blog_entry.event_id,
    }


@pytest.mark.django_db
def test_unauthenticated_cannot_read_non_public_entry(api_client, blog_entry):
    """Test unauthenticated users cannot read a non-public blog entry"""
    result = api_client.get(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 404

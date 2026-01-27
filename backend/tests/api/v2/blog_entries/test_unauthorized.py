import pytest
from django.conf import settings

BASE_URL = "/api/v2/blog_entries/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 403),
        ("DELETE", 403),
        ("PATCH", 403),
        ("PUT", 403),
    ],
)
def test_unauthorized_write_denied(user_api_client, public_blog_entry, method, status):
    """Test unauthorized write access is denied"""
    url = f"{BASE_URL}{public_blog_entry.id}/" if method != "POST" else BASE_URL
    assert user_api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_can_read_public_entries_list(user_api_client, public_blog_entry, blog_entry):
    """Test unauthorized users can read public blog entries list"""
    result = user_api_client.get(BASE_URL)
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
def test_unauthorized_cannot_read_non_public_entry(user_api_client, blog_entry):
    """Test unauthorized users cannot read a non-public blog entry"""
    result = user_api_client.get(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 404

import json
from datetime import datetime, timezone
from unittest.mock import ANY

import pytest

from Instanssi.ext_blog.models import BlogEntry

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
def test_blog_get_entries(super_api_client, blog_entry):
    """Test GET for all items"""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    # We test output once here -- no point in testing serializer in other tests again.
    item = result.data[0]
    assert datetime.fromisoformat(item["date"]) == blog_entry.date
    assert item == {
        "id": blog_entry.id,
        "user": blog_entry.user_id,
        "date": ANY,
        "title": blog_entry.title,
        "text": blog_entry.text,
        "public": blog_entry.public,
        "event": blog_entry.event_id,
    }


@pytest.mark.django_db
def test_blog_get_entry_by_id(super_api_client, blog_entry):
    """Test GET for specific ID"""
    result = super_api_client.get(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 200


@pytest.mark.django_db
def test_blog_post_new(super_api_client, event, super_user):
    """Make sure POST works"""
    result = super_api_client.post(
        BASE_URL,
        dict(
            title="TITLE",
            text="TEXT",
            event=event.id,
            user=super_user.id,
            date=datetime.now(timezone.utc).isoformat(),
        ),
    )
    assert result.status_code == 201


@pytest.mark.django_db
def test_blog_patch_old(super_api_client, event, blog_entry):
    """Make sure PATCH works"""
    result = super_api_client.patch(
        f"{BASE_URL}{blog_entry.id}/",
        dict(
            title="NEW TITLE",
            text="NEW TEXT",
        ),
    )
    assert result.status_code == 200


@pytest.mark.django_db
def test_blog_put_old(super_api_client, event, blog_entry):
    """Make sure PUT works"""
    result = super_api_client.put(
        f"{BASE_URL}{blog_entry.id}/",
        dict(
            title="NEW TITLE",
            text="NEW TEXT",
            date=datetime.now(timezone.utc).isoformat(),
            user=blog_entry.user.id,
            event=blog_entry.event.id,
        ),
    )
    assert result.status_code == 200


@pytest.mark.django_db
def test_blog_delete_old(super_api_client, event, blog_entry):
    """Make sure DELETE works"""
    result = super_api_client.delete(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 204
    assert BlogEntry.objects.filter(id=blog_entry.id).first() is None

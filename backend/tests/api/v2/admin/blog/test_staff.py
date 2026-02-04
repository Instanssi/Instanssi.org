from unittest.mock import ANY

import pytest
from django.conf import settings

from Instanssi.ext_blog.models import BlogEntry

BASE_URL = "/api/v2/admin/blog/"


@pytest.mark.django_db
def test_staff_can_see_all_entries(super_api_client, blog_entry, public_blog_entry):
    """Test staff can see both public and non-public blog entries (ordered by -id)"""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    # Default ordering is -id (newest first)
    assert result.data == [
        {
            "id": public_blog_entry.id,
            "user": public_blog_entry.user_id,
            "created_by": public_blog_entry.user.get_username(),
            "date": public_blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
            "title": "Public test post",
            "text": "This is a public test blog entry.",
            "public": True,
            "event": public_blog_entry.event_id,
        },
        {
            "id": blog_entry.id,
            "user": blog_entry.user_id,
            "created_by": blog_entry.user.get_username(),
            "date": blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
            "title": "Test post",
            "text": "This is a non-public test blog entry.",
            "public": False,
            "event": blog_entry.event_id,
        },
    ]


@pytest.mark.django_db
def test_staff_can_read_non_public_entry(super_api_client, blog_entry):
    """Test staff can read a non-public blog entry"""
    result = super_api_client.get(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 200
    assert result.data == {
        "id": blog_entry.id,
        "user": blog_entry.user_id,
        "created_by": blog_entry.user.get_username(),
        "date": blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "Test post",
        "text": "This is a non-public test blog entry.",
        "public": False,
        "event": blog_entry.event_id,
    }


@pytest.mark.django_db
def test_staff_post_new(super_api_client, event, super_user):
    """Test POST works"""
    result = super_api_client.post(
        BASE_URL,
        {
            "title": "New Post",
            "text": "New post content.",
            "event": event.id,
        },
    )
    assert result.status_code == 201
    assert result.data == {
        "id": result.data["id"],
        "user": super_user.id,
        "created_by": super_user.get_username(),
        "date": ANY,
        "title": "New Post",
        "text": "New post content.",
        "public": False,
        "event": event.id,
    }


@pytest.mark.django_db
def test_staff_patch(super_api_client, blog_entry):
    """Test PATCH works"""
    result = super_api_client.patch(
        f"{BASE_URL}{blog_entry.id}/",
        {
            "title": "Updated Title",
            "text": "Updated content.",
        },
    )
    assert result.status_code == 200
    assert result.data == {
        "id": blog_entry.id,
        "user": blog_entry.user_id,
        "created_by": blog_entry.user.get_username(),
        "date": blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "Updated Title",
        "text": "Updated content.",
        "public": False,
        "event": blog_entry.event_id,
    }


@pytest.mark.django_db
def test_staff_put(super_api_client, blog_entry):
    """Test PUT works"""
    result = super_api_client.put(
        f"{BASE_URL}{blog_entry.id}/",
        {
            "title": "Replaced Title",
            "text": "Replaced content.",
            "event": blog_entry.event_id,
        },
    )
    assert result.status_code == 200
    blog_entry.refresh_from_db()
    assert result.data == {
        "id": blog_entry.id,
        "user": blog_entry.user_id,
        "created_by": blog_entry.user.get_username(),
        "date": blog_entry.date.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "Replaced Title",
        "text": "Replaced content.",
        "public": False,
        "event": blog_entry.event_id,
    }


@pytest.mark.django_db
def test_staff_delete(super_api_client, blog_entry):
    """Test DELETE works"""
    result = super_api_client.delete(f"{BASE_URL}{blog_entry.id}/")
    assert result.status_code == 204
    assert BlogEntry.objects.filter(id=blog_entry.id).first() is None

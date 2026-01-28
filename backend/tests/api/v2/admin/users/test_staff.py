"""Tests for staff access to the users endpoint."""

from unittest.mock import ANY

import pytest
from django.conf import settings
from django.contrib.auth.models import User

BASE_URL = "/api/v2/admin/users/"


@pytest.mark.django_db
def test_users_get_users(super_api_client, super_user):
    """Test GET for all items"""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    # We test output once here -- no point in testing serializer in other tests again.
    assert result.data == [
        {
            "id": super_user.id,
            "first_name": super_user.first_name,
            "last_name": super_user.last_name,
            "date_joined": super_user.date_joined.astimezone(settings.ZONE_INFO).isoformat(),
            "email": super_user.email,
            "username": super_user.username,
            "user_permissions": [],
            "groups": [],
            "is_superuser": super_user.is_superuser,
            "is_active": super_user.is_active,
        }
    ]


@pytest.mark.django_db
def test_users_get_entry_by_id(super_api_client, base_user):
    """Test GET for specific ID"""
    result = super_api_client.get(f"{BASE_URL}{base_user.id}/")
    assert result.status_code == 200
    assert "first_name" in result.data


@pytest.mark.django_db
def test_users_post_new(super_api_client):
    """Make sure POST works"""
    req = dict(
        first_name="first_name",
        last_name="last_name",
        username="username",
        email="email@test.com",
        groups=[],
    )
    result = super_api_client.post(BASE_URL, req)
    assert result.status_code == 201
    assert result.json() == {
        "id": ANY,
        "is_superuser": False,
        "user_permissions": [],
        "date_joined": ANY,
        "is_active": True,
        **req,
    }


@pytest.mark.django_db
def test_users_patch_old(super_api_client, base_user):
    """Make sure PATCH works"""
    result = super_api_client.patch(
        f"{BASE_URL}{base_user.id}/",
        dict(
            first_name="new first name",
            last_name="new last name",
        ),
    )
    assert result.status_code == 200
    assert result.data["first_name"] == "new first name"
    assert result.data["last_name"] == "new last name"


@pytest.mark.django_db
def test_users_put_old(super_api_client, base_user):
    """Make sure PUT works"""
    req = dict(
        first_name="new_first_name",
        last_name="new_last_name",
        username="new_username",
        email="new_email@test.com",
        groups=[],
    )
    result = super_api_client.put(f"{BASE_URL}{base_user.id}/", req)
    assert result.status_code == 200
    assert result.json() == {
        "id": base_user.id,
        "is_superuser": base_user.is_superuser,
        "user_permissions": [],
        "date_joined": base_user.date_joined.astimezone(settings.ZONE_INFO).isoformat(),
        "is_active": base_user.is_active,
        **req,
    }


@pytest.mark.django_db
def test_users_delete_old(super_api_client, base_user):
    """Make sure DELETE works"""
    result = super_api_client.delete(f"{BASE_URL}{base_user.id}/")
    assert result.status_code == 204
    assert User.objects.filter(id=base_user.id).first() is None

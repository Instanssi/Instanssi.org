"""Tests for staff access to the users endpoint."""

from unittest.mock import ANY

import pytest
from django.conf import settings

from Instanssi.users.models import User

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
            "is_system": super_user.is_system,
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
        "is_system": False,
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
        "is_system": base_user.is_system,
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


@pytest.mark.django_db
def test_system_user_cannot_be_patched(super_api_client, create_user):
    """System users cannot be updated via PATCH"""
    system_user = create_user(is_system=True)
    result = super_api_client.patch(
        f"{BASE_URL}{system_user.id}/",
        dict(first_name="hacked"),
    )
    assert result.status_code == 403


@pytest.mark.django_db
def test_system_user_cannot_be_put(super_api_client, create_user):
    """System users cannot be updated via PUT"""
    system_user = create_user(is_system=True)
    result = super_api_client.put(
        f"{BASE_URL}{system_user.id}/",
        dict(
            first_name="hacked",
            last_name="hacked",
            username="hacked",
            email="hacked@test.com",
            groups=[],
        ),
    )
    assert result.status_code == 403


@pytest.mark.django_db
def test_system_user_cannot_be_deleted(super_api_client, create_user):
    """System users cannot be deleted"""
    system_user = create_user(is_system=True)
    result = super_api_client.delete(f"{BASE_URL}{system_user.id}/")
    assert result.status_code == 403
    assert User.objects.filter(id=system_user.id).exists()


@pytest.mark.django_db
def test_is_system_is_read_only(super_api_client, base_user):
    """The is_system field cannot be set via the API"""
    result = super_api_client.patch(
        f"{BASE_URL}{base_user.id}/",
        dict(is_system=True),
    )
    assert result.status_code == 200
    base_user.refresh_from_db()
    assert base_user.is_system is False


@pytest.mark.django_db
def test_superuser_can_set_is_staff(super_api_client, base_user):
    """Superusers can change the is_staff field"""
    assert base_user.is_staff is False
    result = super_api_client.patch(
        f"{BASE_URL}{base_user.id}/",
        dict(is_staff=True),
    )
    assert result.status_code == 200
    base_user.refresh_from_db()
    assert base_user.is_staff is True


@pytest.mark.django_db
def test_non_superuser_cannot_set_is_staff(api_client, create_user, password, base_user):
    """Non-superuser staff cannot change the is_staff field"""
    staff = create_user(
        is_staff=True,
        permissions=["users.view_user", "users.change_user"],
    )
    api_client.login(username=staff.username, password=password)
    result = api_client.patch(
        f"{BASE_URL}{base_user.id}/",
        dict(is_staff=True),
    )
    assert result.status_code == 200
    base_user.refresh_from_db()
    assert base_user.is_staff is False

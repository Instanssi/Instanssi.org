"""Tests for staff access to the groups endpoint."""

import pytest
from django.contrib.auth.models import Group

BASE_URL = "/api/v2/admin/groups/"


@pytest.mark.django_db
def test_groups_unauthenticated(api_client):
    """Unauthenticated users cannot access groups"""
    result = api_client.get(BASE_URL)
    assert result.status_code == 401


@pytest.mark.django_db
def test_groups_unauthorized(user_api_client):
    """Authenticated non-staff users cannot access groups"""
    result = user_api_client.get(BASE_URL)
    assert result.status_code == 403


@pytest.mark.django_db
def test_groups_list(super_api_client):
    """Superusers can list all groups"""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    names = {g["name"] for g in result.data}
    assert {"staff_defaults", "store", "tokens"} <= names
    # Every group has an id
    for group in result.data:
        assert "id" in group
        assert "name" in group


@pytest.mark.django_db
def test_groups_retrieve(super_api_client):
    """Superusers can retrieve a single group"""
    group = Group.objects.get(name="staff_defaults")
    result = super_api_client.get(f"{BASE_URL}{group.id}/")
    assert result.status_code == 200
    assert result.data == {"id": group.id, "name": "staff_defaults"}


@pytest.mark.django_db
def test_groups_staff_with_permission(api_client, create_user, password):
    """Staff users with auth.view_group can list groups"""
    staff = create_user(is_staff=True, permissions=["auth.view_group"])
    api_client.login(email=staff.email, password=password)
    result = api_client.get(BASE_URL)
    assert result.status_code == 200


@pytest.mark.django_db
def test_groups_staff_without_permission(api_client, create_user, password):
    """Staff users without auth.view_group cannot list groups"""
    staff = create_user(is_staff=True)
    api_client.login(email=staff.email, password=password)
    result = api_client.get(BASE_URL)
    assert result.status_code == 403


@pytest.mark.django_db
def test_groups_read_only(super_api_client):
    """Groups endpoint is read-only; POST should be rejected"""
    result = super_api_client.post(BASE_URL, dict(name="new_group"))
    assert result.status_code == 405

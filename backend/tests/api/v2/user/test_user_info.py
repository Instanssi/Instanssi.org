import pytest
from django.conf import settings
from django.contrib.auth.models import Group, Permission

BASE_URL = "/api/v2/user_info/"


@pytest.mark.django_db
def test_unauthenticated_user_info(api_client):
    """Test unauthenticated access (Not logged in)"""
    assert api_client.get(BASE_URL).status_code == 401


@pytest.mark.django_db
def test_authenticated_user_info(auth_client, base_user):
    """Test authenticated access, and make sure serializer spits out correct looking stuff."""
    response = auth_client.get(BASE_URL)
    assert response.status_code == 200
    assert response.data == [
        {
            "id": base_user.id,
            "username": base_user.username,
            "first_name": base_user.first_name,
            "last_name": base_user.last_name,
            "email": base_user.email,
            "user_permissions": [],
            "date_joined": base_user.date_joined.astimezone(settings.ZONE_INFO).isoformat(),
            "is_superuser": base_user.is_superuser,
        }
    ]


@pytest.mark.django_db
def test_user_info_includes_group_permissions(auth_client, base_user):
    """Test that permissions from groups are included in user_permissions."""
    # Create a group with a permission
    group = Group.objects.create(name="Test Group")
    permission = Permission.objects.get(codename="add_event")
    group.permissions.add(permission)

    # Add user to the group
    base_user.groups.add(group)

    response = auth_client.get(BASE_URL)
    assert response.status_code == 200
    permissions = response.data[0]["user_permissions"]
    assert permissions == ["add_event"]

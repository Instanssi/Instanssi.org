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
    assert response.data == {
        "id": base_user.id,
        "username": base_user.username,
        "first_name": base_user.first_name,
        "last_name": base_user.last_name,
        "email": base_user.email,
        "user_permissions": [],
        "is_staff": base_user.is_staff,
        "is_superuser": base_user.is_superuser,
        "date_joined": base_user.date_joined.astimezone(settings.ZONE_INFO).isoformat(),
        "language": "",
        "notify_vote_code_requests": True,
        "notify_program_events": True,
        "notify_compo_starts": True,
        "notify_competition_starts": True,
    }


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
    assert response.data["user_permissions"] == ["add_event"]


@pytest.mark.django_db
def test_unauthenticated_patch(api_client):
    """Test that unauthenticated PATCH is rejected."""
    assert api_client.patch(BASE_URL, {"language": "fi"}).status_code == 401


@pytest.mark.django_db
def test_patch_language(auth_client, base_user):
    """Test setting language preference via PATCH."""
    response = auth_client.patch(BASE_URL, {"language": "fi"}, format="json")
    assert response.status_code == 200
    assert response.data["language"] == "fi"
    base_user.refresh_from_db()
    assert base_user.language == "fi"


@pytest.mark.django_db
def test_patch_language_clear(auth_client, base_user):
    """Test clearing language preference via PATCH."""
    base_user.language = "fi"
    base_user.save()

    response = auth_client.patch(BASE_URL, {"language": ""}, format="json")
    assert response.status_code == 200
    assert response.data["language"] == ""
    base_user.refresh_from_db()
    assert base_user.language == ""


@pytest.mark.django_db
def test_patch_language_invalid(auth_client, base_user):
    """Test that invalid language values are rejected."""
    response = auth_client.patch(BASE_URL, {"language": "xx"}, format="json")
    assert response.status_code == 400


@pytest.mark.django_db
def test_patch_first_name_and_last_name(auth_client, base_user):
    """Test updating first_name and last_name via PATCH."""
    response = auth_client.patch(BASE_URL, {"first_name": "Updated", "last_name": "Name"}, format="json")
    assert response.status_code == 200
    assert response.data["first_name"] == "Updated"
    assert response.data["last_name"] == "Name"
    base_user.refresh_from_db()
    assert base_user.first_name == "Updated"
    assert base_user.last_name == "Name"


@pytest.mark.django_db
def test_patch_does_not_change_read_only_fields(auth_client, base_user):
    """Test that PATCH cannot change read-only fields."""
    original_username = base_user.username
    original_email = base_user.email

    response = auth_client.patch(
        BASE_URL,
        {"is_superuser": True, "username": "hacked", "email": "hacked@example.com"},
        format="json",
    )
    assert response.status_code == 200
    base_user.refresh_from_db()
    assert base_user.is_superuser is False
    assert base_user.username == original_username
    assert base_user.email == original_email


# --- Notification preference tests ---


@pytest.mark.django_db
def test_user_sees_notification_fields(auth_client):
    """All authenticated users should see notification preference fields in the response."""
    response = auth_client.get(BASE_URL)
    assert response.status_code == 200
    assert response.data["notify_vote_code_requests"] is True
    assert response.data["notify_program_events"] is True
    assert response.data["notify_compo_starts"] is True
    assert response.data["notify_competition_starts"] is True


@pytest.mark.django_db
def test_can_patch_notification_preferences(auth_client, base_user):
    """Authenticated users can update notification preferences via PATCH."""
    response = auth_client.patch(
        BASE_URL,
        {"notify_vote_code_requests": False},
        format="json",
    )
    assert response.status_code == 200
    assert response.data["notify_vote_code_requests"] is False
    assert response.data["notify_program_events"] is True
    base_user.refresh_from_db()
    assert base_user.notify_vote_code_requests is False

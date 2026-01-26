import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/uploads/files/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),  # Staff only - no public read
        ("POST", 403),  # Create denied
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_uploads_list(user_api_client, event, method, status):
    """Test unauthorized access to list endpoint (logged in but no permissions)."""
    base_url = get_base_url(event.id)
    assert user_api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),  # Staff only - no public read
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_uploads_nonexistent_detail(user_api_client, event, method, status):
    """Test unauthorized access to non-existent upload detail endpoint."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert user_api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),  # Staff only - no public read
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_uploads_existing_detail(user_api_client, uploaded_file, method, status):
    """Test unauthorized access to existing upload detail endpoint."""
    base_url = get_base_url(uploaded_file.event_id)
    url = f"{base_url}{uploaded_file.id}/"
    assert user_api_client.generic(method, url).status_code == status

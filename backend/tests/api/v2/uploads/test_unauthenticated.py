import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/uploads/files/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),  # Staff only - no public read
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_uploads_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),  # Staff only - no public read
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_uploads_nonexistent_detail(api_client, event, method, status):
    """Test unauthenticated access to non-existent upload detail endpoint."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),  # Staff only - no public read
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_uploads_existing_detail(api_client, uploaded_file, method, status):
    """Test unauthenticated access to existing upload detail endpoint."""
    base_url = get_base_url(uploaded_file.event_id)
    url = f"{base_url}{uploaded_file.id}/"
    assert api_client.generic(method, url).status_code == status

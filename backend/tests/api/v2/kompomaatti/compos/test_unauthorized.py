import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/compos/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active compos
        ("POST", 403),  # Create denied
        ("PUT", 403),  # Not allowed on list
        ("PATCH", 403),  # Not allowed on list
        ("DELETE", 403),  # Not allowed on list
    ],
)
def test_unauthorized_compos_list(auth_client, event, method, status):
    """Test unauthorized access to list endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    assert auth_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if compo doesn't exist
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_compos_nonexistent_detail(auth_client, event, method, status):
    """Test unauthorized access to non-existent compo detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active compo
        ("POST", 403),  # Not allowed on detail
        ("PUT", 403),  # Replace denied
        ("PATCH", 403),  # Update denied
        ("DELETE", 403),  # Delete denied
    ],
)
def test_unauthorized_compos_existing_detail(auth_client, event, open_compo, method, status):
    """Test unauthorized access to existing compo detail endpoint (Logged in, but no permissions)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{open_compo.id}/"
    assert auth_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_unauthorized_can_read_active_compos(auth_client, votable_compo):
    """Test that users without permissions can read active compos"""
    base_url = get_base_url(votable_compo.event_id)
    # List active compos
    req = auth_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view of active compo
    req = auth_client.get(f"{base_url}{votable_compo.id}/")
    assert req.status_code == 200
    assert req.data["id"] == votable_compo.id

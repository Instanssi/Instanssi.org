import pytest


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/compos/"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access for active compos
        ("POST", 401),  # Create denied
        ("PUT", 401),  # Not allowed on list
        ("PATCH", 401),  # Not allowed on list
        ("DELETE", 401),  # Not allowed on list
    ],
)
def test_unauthenticated_compos_list(api_client, event, method, status):
    """Test unauthenticated access to list endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    assert api_client.generic(method, base_url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 404),  # Returns 404 if compo doesn't exist
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_compos_nonexistent_detail(api_client, event, method, status):
    """Test unauthenticated access to non-existent compo detail endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}999999/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),  # Public read access to existing active compo
        ("POST", 401),  # Not allowed on detail
        ("PUT", 401),  # Replace denied
        ("PATCH", 401),  # Update denied
        ("DELETE", 401),  # Delete denied
    ],
)
def test_unauthenticated_compos_existing_detail(api_client, event, open_compo, method, status):
    """Test unauthenticated access to existing compo detail endpoint (Not logged in)."""
    base_url = get_base_url(event.id)
    url = f"{base_url}{open_compo.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_anonymous_can_read_active_compos(api_client, open_compo):
    """Test that anonymous users can read active compos"""
    base_url = get_base_url(open_compo.event_id)
    # List active compos
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1
    # Detail view of active compo
    req = api_client.get(f"{base_url}{open_compo.id}/")
    assert req.status_code == 200
    assert req.data["id"] == open_compo.id


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_compos(api_client, inactive_compo):
    """Test that anonymous users cannot see inactive compos"""
    base_url = get_base_url(inactive_compo.event_id)

    # Anonymous users should not see inactive compos in list
    anon_req = api_client.get(base_url)
    assert anon_req.status_code == 200
    anon_ids = [compo["id"] for compo in anon_req.data]
    assert inactive_compo.id not in anon_ids

    # Anonymous users should get 404 when trying to access inactive compo detail
    detail_req = api_client.get(f"{base_url}{inactive_compo.id}/")
    assert detail_req.status_code == 404

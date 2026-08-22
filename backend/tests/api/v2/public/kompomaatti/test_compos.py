import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/kompomaatti/compos/"


@pytest.mark.django_db
def test_anonymous_can_list_active_compos(api_client, open_compo):
    """Test that anonymous users can list active compos."""
    base_url = get_base_url(open_compo.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    compo_ids = [c["id"] for c in req.data]
    assert open_compo.id in compo_ids


@pytest.mark.django_db
def test_anonymous_can_get_active_compo_detail(api_client, open_compo):
    """Test that anonymous users can get active compo details."""
    base_url = get_base_url(open_compo.event_id)
    req = api_client.get(f"{base_url}{open_compo.id}/")
    assert req.status_code == 200
    assert req.data["id"] == open_compo.id


@pytest.mark.django_db
def test_compo_detail_contains_entry_submission_fields(api_client, open_compo):
    """Fields needed by the kompomaatti frontend entry forms are exposed."""
    base_url = get_base_url(open_compo.event_id)
    req = api_client.get(f"{base_url}{open_compo.id}/")
    assert req.status_code == 200
    assert req.data["max_entry_size"] == open_compo.max_entry_size
    assert req.data["max_source_size"] == open_compo.max_source_size
    assert req.data["max_image_size"] == open_compo.max_image_size
    assert req.data["entry_format_list"] == open_compo.entry_format_list
    assert req.data["source_format_list"] == open_compo.source_format_list
    assert req.data["image_format_list"] == open_compo.image_format_list
    assert req.data["is_imagefile_allowed"] == open_compo.is_imagefile_allowed
    assert req.data["is_imagefile_required"] == open_compo.is_imagefile_required
    assert req.data["show_voting_results"] == open_compo.show_voting_results


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_compos(api_client, inactive_compo):
    """Test that inactive compos are not visible."""
    base_url = get_base_url(inactive_compo.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    compo_ids = [c["id"] for c in req.data]
    assert inactive_compo.id not in compo_ids

    # Not in detail
    req = api_client.get(f"{base_url}{inactive_compo.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("POST", 405),
        ("PUT", 405),
        ("PATCH", 405),
        ("DELETE", 405),
    ],
)
def test_anonymous_cannot_modify_compos(api_client, open_compo, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(open_compo.event_id)
    url = f"{base_url}{open_compo.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_compos_not_in_list(api_client, hidden_event, hidden_event_compo):
    """Compos from hidden events should not appear in the list."""
    base_url = get_base_url(hidden_event.id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0


@pytest.mark.django_db
def test_hidden_event_compo_detail_returns_404(api_client, hidden_event, hidden_event_compo):
    """Compo detail from hidden event should return 404."""
    base_url = get_base_url(hidden_event.id)
    req = api_client.get(f"{base_url}{hidden_event_compo.id}/")
    assert req.status_code == 404

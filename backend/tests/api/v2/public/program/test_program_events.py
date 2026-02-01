import pytest


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/program/events/"


@pytest.mark.django_db
def test_anonymous_can_list_active_program_events(api_client, program_event):
    """Test that anonymous users can list active program events."""
    base_url = get_base_url(program_event.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [pe["id"] for pe in req.data]
    assert program_event.id in ids


@pytest.mark.django_db
def test_anonymous_can_get_active_program_event_detail(api_client, program_event):
    """Test that anonymous users can get active program event details."""
    base_url = get_base_url(program_event.event_id)
    req = api_client.get(f"{base_url}{program_event.id}/")
    assert req.status_code == 200
    assert req.data["id"] == program_event.id


@pytest.mark.django_db
def test_anonymous_cannot_see_inactive_program_events(api_client, inactive_program_event):
    """Test that inactive program events are not visible."""
    base_url = get_base_url(inactive_program_event.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    ids = [pe["id"] for pe in req.data]
    assert inactive_program_event.id not in ids

    # Not in detail
    req = api_client.get(f"{base_url}{inactive_program_event.id}/")
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
def test_anonymous_cannot_modify_program_events(api_client, program_event, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(program_event.event_id)
    url = f"{base_url}{program_event.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_program_not_in_list(api_client, hidden_event, hidden_event_program):
    """Program events from hidden events should not appear in the list."""
    base_url = get_base_url(hidden_event.id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0

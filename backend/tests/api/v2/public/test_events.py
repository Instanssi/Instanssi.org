import pytest

BASE_URL = "/api/v2/public/events/"


@pytest.mark.django_db
def test_anonymous_can_list_events(api_client, event):
    """Test that anonymous users can list events."""
    req = api_client.get(BASE_URL)
    assert req.status_code == 200
    event_ids = [e["id"] for e in req.data]
    assert event.id in event_ids


@pytest.mark.django_db
def test_anonymous_can_get_event_detail(api_client, event):
    """Test that anonymous users can get event details."""
    req = api_client.get(f"{BASE_URL}{event.id}/")
    assert req.status_code == 200
    assert req.data["id"] == event.id
    assert req.data["name"] == event.name


@pytest.mark.django_db
def test_anonymous_can_filter_by_archived(api_client, event, archived_event):
    """Test that anonymous users can filter events by archived status."""
    req = api_client.get(f"{BASE_URL}?archived=true")
    assert req.status_code == 200
    event_ids = [e["id"] for e in req.data]
    assert archived_event.id in event_ids
    assert event.id not in event_ids


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
def test_anonymous_cannot_modify_events(api_client, event, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    url = f"{BASE_URL}{event.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_not_in_list(api_client, event, hidden_event):
    """Hidden events should not appear in the public events list."""
    req = api_client.get(BASE_URL)
    assert req.status_code == 200
    event_ids = [e["id"] for e in req.data]
    assert event.id in event_ids
    assert hidden_event.id not in event_ids


@pytest.mark.django_db
def test_hidden_event_detail_returns_404(api_client, hidden_event):
    """Hidden event detail should return 404."""
    req = api_client.get(f"{BASE_URL}{hidden_event.id}/")
    assert req.status_code == 404

"""Tests for staff access to the events endpoint."""

from datetime import date

import pytest

from Instanssi.kompomaatti.models import Event

BASE_URL = "/api/v2/admin/events/"


@pytest.mark.django_db
def test_events_get_entries(super_api_client, event):
    """Test GET for all items"""
    result = super_api_client.get(BASE_URL)
    assert result.status_code == 200
    # We test output once here -- no point in testing serializer in other tests again.
    assert result.data == [
        {
            "id": event.id,
            "name": event.name,
            "tag": event.tag,
            "date": event.date.isoformat(),
            "archived": event.archived,
            "hidden": event.hidden,
            "mainurl": event.mainurl,
        }
    ]


@pytest.mark.django_db
def test_events_get_entry_by_id(super_api_client, event):
    """Test GET for specific ID"""
    result = super_api_client.get(f"{BASE_URL}{event.id}/")
    assert result.status_code == 200
    assert result.data == {
        "id": event.id,
        "name": event.name,
        "tag": event.tag,
        "date": event.date.isoformat(),
        "archived": event.archived,
        "hidden": event.hidden,
        "mainurl": event.mainurl,
    }


@pytest.mark.django_db
def test_events_post_new(super_api_client):
    """Make sure POST works"""
    dt = date.today().isoformat()
    result = super_api_client.post(
        BASE_URL,
        dict(
            name="NAME",
            tag="2024",
            date=dt,
            archived=False,
            mainurl="https://localhost/2024",
        ),
    )
    assert result.status_code == 201
    assert result.data == {
        "id": result.data["id"],
        "name": "NAME",
        "tag": "2024",
        "date": dt,
        "archived": False,
        "hidden": False,
        "mainurl": "https://localhost/2024",
    }


@pytest.mark.django_db
def test_events_patch_old(super_api_client, event):
    """Make sure PATCH works"""
    result = super_api_client.patch(
        f"{BASE_URL}{event.id}/",
        dict(
            name="NEW NAME",
            tag="2030",
        ),
    )
    assert result.status_code == 200
    assert result.data == {
        "id": event.id,
        "name": "NEW NAME",
        "tag": "2030",
        "date": event.date.isoformat(),
        "archived": event.archived,
        "hidden": event.hidden,
        "mainurl": event.mainurl,
    }


@pytest.mark.django_db
def test_events_put_old(super_api_client, event):
    """Make sure PUT works"""
    dt = date.today().isoformat()
    result = super_api_client.put(
        f"{BASE_URL}{event.id}/",
        dict(
            name="NEW NAME",
            tag="2030",
            date=dt,
            archived=True,
            mainurl="https://localhost/2030",
        ),
    )
    assert result.status_code == 200
    assert result.data == {
        "id": event.id,
        "name": "NEW NAME",
        "tag": "2030",
        "date": dt,
        "archived": True,
        "hidden": False,
        "mainurl": "https://localhost/2030",
    }


@pytest.mark.django_db
def test_events_delete_old(super_api_client, event):
    """Make sure DELETE works"""
    result = super_api_client.delete(f"{BASE_URL}{event.id}/")
    assert result.status_code == 204
    assert Event.objects.filter(id=event.id).first() is None


@pytest.mark.django_db
def test_admin_can_list_hidden_events(staff_api_client, event, hidden_event):
    """Admin should see hidden events in the list."""
    req = staff_api_client.get(BASE_URL)
    assert req.status_code == 200
    event_ids = [e["id"] for e in req.data]
    assert event.id in event_ids
    assert hidden_event.id in event_ids


@pytest.mark.django_db
def test_admin_can_get_hidden_event_detail(staff_api_client, hidden_event):
    """Admin should be able to access hidden event details."""
    req = staff_api_client.get(f"{BASE_URL}{hidden_event.id}/")
    assert req.status_code == 200
    assert req.data["id"] == hidden_event.id
    assert req.data["hidden"] is True


@pytest.mark.django_db
def test_admin_can_toggle_hidden_field(staff_api_client, event):
    """Admin should be able to toggle the hidden field."""
    # Initially not hidden
    assert event.hidden is False

    # Set to hidden
    req = staff_api_client.patch(
        f"{BASE_URL}{event.id}/",
        data={"hidden": True},
    )
    assert req.status_code == 200
    assert req.data["hidden"] is True

    # Verify in database
    event.refresh_from_db()
    assert event.hidden is True

    # Set back to visible
    req = staff_api_client.patch(
        f"{BASE_URL}{event.id}/",
        data={"hidden": False},
    )
    assert req.status_code == 200
    assert req.data["hidden"] is False

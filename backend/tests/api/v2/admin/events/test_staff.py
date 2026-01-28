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
        "mainurl": "https://localhost/2030",
    }


@pytest.mark.django_db
def test_events_delete_old(super_api_client, event):
    """Make sure DELETE works"""
    result = super_api_client.delete(f"{BASE_URL}{event.id}/")
    assert result.status_code == 204
    assert Event.objects.filter(id=event.id).first() is None

from datetime import timedelta

import pytest
from django.utils import timezone

from Instanssi.kompomaatti.models import Compo


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/compos/"


@pytest.mark.django_db
def test_staff_can_list_compos(staff_api_client, open_compo, votable_compo):
    """Test that staff can list all compos"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 2


@pytest.mark.django_db
def test_staff_can_get_compo_detail(staff_api_client, open_compo):
    """Test that staff can get compo details"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.get(f"{base_url}{open_compo.id}/")
    assert req.status_code == 200
    assert req.data["id"] == open_compo.id
    assert req.data["name"] == open_compo.name
    assert req.data["event"] == open_compo.event_id


@pytest.mark.django_db
def test_staff_can_create_compo(staff_api_client, event):
    """Test that staff can create a new compo"""
    base_url = get_base_url(event.id)
    now = timezone.now()
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "name": "New Test Compo",
            "description": "A brand new compo",
            "adding_end": (now + timedelta(hours=1)).isoformat(),
            "editing_end": (now + timedelta(hours=2)).isoformat(),
            "compo_start": (now + timedelta(hours=3)).isoformat(),
            "voting_start": (now + timedelta(hours=4)).isoformat(),
            "voting_end": (now + timedelta(hours=8)).isoformat(),
        },
    )
    assert req.status_code == 201
    assert req.data["name"] == "New Test Compo"


@pytest.mark.django_db
def test_staff_can_update_compo(staff_api_client, open_compo):
    """Test that staff can update a compo"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.patch(f"{base_url}{open_compo.id}/", {"name": "Updated Compo Name"})
    assert req.status_code == 200
    assert req.data["name"] == "Updated Compo Name"


@pytest.mark.django_db
def test_staff_can_delete_compo(staff_api_client, open_compo):
    """Test that staff can delete a compo"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.delete(f"{base_url}{open_compo.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_filter_by_event(staff_api_client, event, open_compo):
    """Test filtering compos by event"""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    for compo in req.data:
        assert compo["event"] == event.id


@pytest.mark.django_db
def test_staff_can_see_inactive_compos(staff_api_client, event):
    """Test that staff can see inactive compos while anonymous users cannot"""
    # Create an inactive compo
    inactive = Compo.objects.create(
        event=event,
        name="Inactive Compo",
        description="This compo is not active",
        active=False,
        adding_end=timezone.now() + timedelta(hours=1),
        editing_end=timezone.now() + timedelta(hours=2),
        compo_start=timezone.now() + timedelta(hours=3),
        voting_start=timezone.now() + timedelta(hours=4),
        voting_end=timezone.now() + timedelta(hours=8),
    )

    base_url = get_base_url(event.id)

    # Staff should see inactive compos
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [compo["id"] for compo in staff_req.data]
    assert inactive.id in staff_ids

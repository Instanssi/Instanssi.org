from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from django.conf import settings


def get_base_url(event_id):
    return f"/api/v2/event/{event_id}/kompomaatti/competitions/"


@pytest.mark.django_db
def test_staff_can_list_competitions(staff_api_client, competition):
    """Test that staff can list all competitions"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_competition_detail(staff_api_client, competition):
    """Test that staff can get competition details"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.get(f"{base_url}{competition.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": competition.id,
        "event": competition.event_id,
        "name": competition.name,
        "description": competition.description,
        "participation_end": competition.participation_end.astimezone(settings.ZONE_INFO).isoformat(),
        "start": competition.start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": competition.end.astimezone(settings.ZONE_INFO).isoformat() if competition.end else None,
        "score_type": competition.score_type,
        "score_sort": competition.score_sort,
        "show_results": competition.show_results,
        "active": competition.active,
        "hide_from_archive": competition.hide_from_archive,
    }


@pytest.mark.django_db
def test_staff_can_create_competition(staff_api_client, event):
    """Test that staff can create a new competition"""
    base_url = get_base_url(event.id)
    participation_end = datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt_tz.utc)
    start = datetime(2025, 6, 15, 14, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "name": "Test Competition",
            "description": "A test competition",
            "participation_end": participation_end.isoformat(),
            "start": start.isoformat(),
            "score_type": "points",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "name": "Test Competition",
        "description": "A test competition",
        "participation_end": participation_end.astimezone(settings.ZONE_INFO).isoformat(),
        "start": start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": None,
        "score_type": "points",
        "score_sort": 0,
        "show_results": False,
        "active": True,
        "hide_from_archive": False,
    }


@pytest.mark.django_db
def test_staff_can_update_competition(staff_api_client, competition):
    """Test that staff can update a competition"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.patch(f"{base_url}{competition.id}/", {"show_results": True})
    assert req.status_code == 200
    assert req.data == {
        "id": competition.id,
        "event": competition.event_id,
        "name": competition.name,
        "description": competition.description,
        "participation_end": competition.participation_end.astimezone(settings.ZONE_INFO).isoformat(),
        "start": competition.start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": competition.end.astimezone(settings.ZONE_INFO).isoformat() if competition.end else None,
        "score_type": competition.score_type,
        "score_sort": competition.score_sort,
        "show_results": True,
        "active": competition.active,
        "hide_from_archive": competition.hide_from_archive,
    }


@pytest.mark.django_db
def test_staff_can_delete_competition(staff_api_client, competition):
    """Test that staff can delete a competition"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.delete(f"{base_url}{competition.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_competitions_filter_by_event(staff_api_client, event, competition):
    """Test filtering competitions by event"""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url, {"event": event.id})
    assert req.status_code == 200
    for comp in req.data:
        assert comp["event"] == event.id


@pytest.mark.django_db
def test_competitions_filter_by_active(staff_api_client, competition):
    """Test filtering competitions by active status"""
    base_url = get_base_url(competition.event_id)
    req = staff_api_client.get(base_url, {"active": "true"})
    assert req.status_code == 200
    for comp in req.data:
        assert comp["active"] is True


@pytest.mark.django_db
def test_staff_can_see_inactive_competitions(staff_api_client, inactive_competition):
    """Test that staff can see inactive competitions while anonymous users cannot"""
    base_url = get_base_url(inactive_competition.event_id)

    # Staff should see inactive competitions
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [comp["id"] for comp in staff_req.data]
    assert inactive_competition.id in staff_ids

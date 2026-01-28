from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from django.conf import settings


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/program/events/"


@pytest.mark.django_db
def test_staff_can_list_program_events(staff_api_client, program_event):
    """Test that staff can list all program events."""
    base_url = get_base_url(program_event.event_id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_staff_can_get_program_event_detail(staff_api_client, program_event):
    """Test that staff can get program event details."""
    base_url = get_base_url(program_event.event_id)
    req = staff_api_client.get(f"{base_url}{program_event.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": program_event.id,
        "event": program_event.event_id,
        "start": program_event.start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": program_event.end.astimezone(settings.ZONE_INFO).isoformat(),
        "title": program_event.title,
        "description": program_event.description,
        "presenters": program_event.presenters,
        "presenters_titles": program_event.presenters_titles,
        "place": program_event.place,
        "icon_original": None,
        "icon_small_url": None,
        "icon2_original": None,
        "icon2_small_url": None,
        "email": program_event.email,
        "home_url": program_event.home_url,
        "twitter_url": program_event.twitter_url,
        "github_url": program_event.github_url,
        "facebook_url": program_event.facebook_url,
        "linkedin_url": program_event.linkedin_url,
        "wiki_url": program_event.wiki_url,
        "event_type": program_event.event_type,
        "active": program_event.active,
    }


@pytest.mark.django_db
def test_staff_can_create_program_event(staff_api_client, event):
    """Test that staff can create a new program event."""
    base_url = get_base_url(event.id)
    start = datetime(2025, 6, 15, 14, 0, 0, tzinfo=dt_tz.utc)
    end = datetime(2025, 6, 15, 15, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "start": start.isoformat(),
            "end": end.isoformat(),
            "title": "New Program Event",
            "description": "A brand new program event",
            "presenters": "Test Presenter",
            "place": "Main Hall",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "start": start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": end.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "New Program Event",
        "description": "A brand new program event",
        "presenters": "Test Presenter",
        "presenters_titles": "",
        "place": "Main Hall",
        "icon_original": None,
        "icon_small_url": None,
        "icon2_original": None,
        "icon2_small_url": None,
        "email": "",
        "home_url": "",
        "twitter_url": "",
        "github_url": "",
        "facebook_url": "",
        "linkedin_url": "",
        "wiki_url": "",
        "event_type": 0,
        "active": True,
    }


@pytest.mark.django_db
def test_staff_can_update_program_event(staff_api_client, program_event):
    """Test that staff can update a program event."""
    base_url = get_base_url(program_event.event_id)
    req = staff_api_client.patch(f"{base_url}{program_event.id}/", {"title": "Updated Program Event"})
    assert req.status_code == 200
    assert req.data == {
        "id": program_event.id,
        "event": program_event.event_id,
        "start": program_event.start.astimezone(settings.ZONE_INFO).isoformat(),
        "end": program_event.end.astimezone(settings.ZONE_INFO).isoformat(),
        "title": "Updated Program Event",
        "description": program_event.description,
        "presenters": program_event.presenters,
        "presenters_titles": program_event.presenters_titles,
        "place": program_event.place,
        "icon_original": None,
        "icon_small_url": None,
        "icon2_original": None,
        "icon2_small_url": None,
        "email": program_event.email,
        "home_url": program_event.home_url,
        "twitter_url": program_event.twitter_url,
        "github_url": program_event.github_url,
        "facebook_url": program_event.facebook_url,
        "linkedin_url": program_event.linkedin_url,
        "wiki_url": program_event.wiki_url,
        "event_type": program_event.event_type,
        "active": program_event.active,
    }


@pytest.mark.django_db
def test_staff_can_delete_program_event(staff_api_client, program_event):
    """Test that staff can delete a program event."""
    base_url = get_base_url(program_event.event_id)
    req = staff_api_client.delete(f"{base_url}{program_event.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_program_events_filter_by_event(staff_api_client, event, program_event):
    """Test that program events are filtered by event."""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    for pe in req.data:
        assert pe["event"] == event.id


@pytest.mark.django_db
def test_staff_can_see_inactive_program_events(staff_api_client, inactive_program_event):
    """Test that staff can see inactive program events."""
    base_url = get_base_url(inactive_program_event.event_id)

    # Staff should see inactive program events in list
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [pe["id"] for pe in staff_req.data]
    assert inactive_program_event.id in staff_ids

    # Staff should be able to access inactive program event detail
    detail_req = staff_api_client.get(f"{base_url}{inactive_program_event.id}/")
    assert detail_req.status_code == 200


@pytest.mark.django_db
def test_search_by_title(staff_api_client, program_event):
    """Test searching program events by title."""
    base_url = get_base_url(program_event.event_id)
    # Get a word from the title to search for
    search_term = program_event.title.split()[0]
    req = staff_api_client.get(f"{base_url}?search={search_term}")
    assert req.status_code == 200
    assert len(req.data) >= 1


@pytest.mark.django_db
def test_program_events_filter_by_active(staff_api_client, program_event, inactive_program_event):
    """Test filtering program events by active status."""
    base_url = get_base_url(program_event.event_id)

    # Filter for active only
    active_req = staff_api_client.get(f"{base_url}?active=true")
    assert active_req.status_code == 200
    active_ids = [pe["id"] for pe in active_req.data]
    assert program_event.id in active_ids
    assert inactive_program_event.id not in active_ids

    # Filter for inactive only
    inactive_req = staff_api_client.get(f"{base_url}?active=false")
    assert inactive_req.status_code == 200
    inactive_ids = [pe["id"] for pe in inactive_req.data]
    assert inactive_program_event.id in inactive_ids
    assert program_event.id not in inactive_ids

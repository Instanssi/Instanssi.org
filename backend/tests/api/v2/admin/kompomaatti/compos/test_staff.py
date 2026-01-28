from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from django.conf import settings


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/kompomaatti/compos/"


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
    assert req.data == {
        "id": open_compo.id,
        "event": open_compo.event_id,
        "name": open_compo.name,
        "description": open_compo.description,
        "adding_end": open_compo.adding_end.astimezone(settings.ZONE_INFO).isoformat(),
        "editing_end": open_compo.editing_end.astimezone(settings.ZONE_INFO).isoformat(),
        "compo_start": open_compo.compo_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_start": open_compo.voting_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_end": open_compo.voting_end.astimezone(settings.ZONE_INFO).isoformat(),
        "entry_sizelimit": open_compo.entry_sizelimit,
        "source_sizelimit": open_compo.source_sizelimit,
        "formats": open_compo.formats,
        "source_formats": open_compo.source_formats,
        "image_formats": open_compo.image_formats,
        "max_source_size": open_compo.max_source_size,
        "max_entry_size": open_compo.max_entry_size,
        "source_format_list": open_compo.source_format_list,
        "entry_format_list": open_compo.entry_format_list,
        "image_format_list": open_compo.image_format_list,
        "active": open_compo.active,
        "show_voting_results": open_compo.show_voting_results,
        "entry_view_type": open_compo.entry_view_type,
        "hide_from_archive": open_compo.hide_from_archive,
        "hide_from_frontpage": open_compo.hide_from_frontpage,
        "is_votable": open_compo.is_votable,
        "thumbnail_pref": open_compo.thumbnail_pref,
    }


@pytest.mark.django_db
def test_staff_can_create_compo(staff_api_client, event):
    """Test that staff can create a new compo"""
    base_url = get_base_url(event.id)
    adding_end = datetime(2025, 6, 15, 12, 0, 0, tzinfo=dt_tz.utc)
    editing_end = datetime(2025, 6, 15, 13, 0, 0, tzinfo=dt_tz.utc)
    compo_start = datetime(2025, 6, 15, 14, 0, 0, tzinfo=dt_tz.utc)
    voting_start = datetime(2025, 6, 15, 15, 0, 0, tzinfo=dt_tz.utc)
    voting_end = datetime(2025, 6, 15, 20, 0, 0, tzinfo=dt_tz.utc)
    req = staff_api_client.post(
        base_url,
        {
            "event": event.id,
            "name": "New Test Compo",
            "description": "A brand new compo",
            "adding_end": adding_end.isoformat(),
            "editing_end": editing_end.isoformat(),
            "compo_start": compo_start.isoformat(),
            "voting_start": voting_start.isoformat(),
            "voting_end": voting_end.isoformat(),
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "name": "New Test Compo",
        "description": "A brand new compo",
        "adding_end": adding_end.astimezone(settings.ZONE_INFO).isoformat(),
        "editing_end": editing_end.astimezone(settings.ZONE_INFO).isoformat(),
        "compo_start": compo_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_start": voting_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_end": voting_end.astimezone(settings.ZONE_INFO).isoformat(),
        "entry_sizelimit": 134217728,
        "source_sizelimit": 134217728,
        "formats": "zip|7z|gz|bz2",
        "source_formats": "zip|7z|gz|bz2",
        "image_formats": "png|jpg",
        "max_source_size": 134217728,
        "max_entry_size": 134217728,
        "source_format_list": ["zip", "7z", "gz", "bz2"],
        "entry_format_list": ["zip", "7z", "gz", "bz2"],
        "image_format_list": ["png", "jpg"],
        "active": True,
        "show_voting_results": False,
        "entry_view_type": 0,
        "hide_from_archive": False,
        "hide_from_frontpage": False,
        "is_votable": True,
        "thumbnail_pref": 2,
    }


@pytest.mark.django_db
def test_staff_can_update_compo(staff_api_client, open_compo):
    """Test that staff can update a compo"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.patch(f"{base_url}{open_compo.id}/", {"name": "Updated Compo Name"})
    assert req.status_code == 200
    assert req.data == {
        "id": open_compo.id,
        "event": open_compo.event_id,
        "name": "Updated Compo Name",
        "description": open_compo.description,
        "adding_end": open_compo.adding_end.astimezone(settings.ZONE_INFO).isoformat(),
        "editing_end": open_compo.editing_end.astimezone(settings.ZONE_INFO).isoformat(),
        "compo_start": open_compo.compo_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_start": open_compo.voting_start.astimezone(settings.ZONE_INFO).isoformat(),
        "voting_end": open_compo.voting_end.astimezone(settings.ZONE_INFO).isoformat(),
        "entry_sizelimit": open_compo.entry_sizelimit,
        "source_sizelimit": open_compo.source_sizelimit,
        "formats": open_compo.formats,
        "source_formats": open_compo.source_formats,
        "image_formats": open_compo.image_formats,
        "max_source_size": open_compo.max_source_size,
        "max_entry_size": open_compo.max_entry_size,
        "source_format_list": open_compo.source_format_list,
        "entry_format_list": open_compo.entry_format_list,
        "image_format_list": open_compo.image_format_list,
        "active": open_compo.active,
        "show_voting_results": open_compo.show_voting_results,
        "entry_view_type": open_compo.entry_view_type,
        "hide_from_archive": open_compo.hide_from_archive,
        "hide_from_frontpage": open_compo.hide_from_frontpage,
        "is_votable": open_compo.is_votable,
        "thumbnail_pref": open_compo.thumbnail_pref,
    }


@pytest.mark.django_db
def test_staff_can_delete_compo(staff_api_client, open_compo):
    """Test that staff can delete a compo"""
    base_url = get_base_url(open_compo.event_id)
    req = staff_api_client.delete(f"{base_url}{open_compo.id}/")
    assert req.status_code == 204


@pytest.mark.django_db
def test_compos_filter_by_event(staff_api_client, event, open_compo):
    """Test filtering compos by event"""
    base_url = get_base_url(event.id)
    req = staff_api_client.get(base_url)
    assert req.status_code == 200
    for compo in req.data:
        assert compo["event"] == event.id


@pytest.mark.django_db
def test_staff_can_see_inactive_compos(staff_api_client, inactive_compo):
    """Test that staff can see inactive compos while anonymous users cannot"""
    base_url = get_base_url(inactive_compo.event_id)

    # Staff should see inactive compos
    staff_req = staff_api_client.get(base_url)
    assert staff_req.status_code == 200
    staff_ids = [compo["id"] for compo in staff_req.data]
    assert inactive_compo.id in staff_ids

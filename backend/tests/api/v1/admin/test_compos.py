from datetime import datetime
from datetime import timezone as dt_tz
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

BASE_URL = "/api/v1/admin/compos/"
FROZEN_TIME = "2025-01-15T12:00:00Z"
_HELSINKI = ZoneInfo("Europe/Helsinki")


def _dt(utc_dt: datetime) -> str:
    """Format a UTC datetime as the serialized string DRF returns (local timezone)."""
    local = utc_dt.astimezone(_HELSINKI)
    s = local.isoformat()
    return s.replace("+00:00", "Z")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 401),
        ("POST", 401),
        ("DELETE", 401),
        ("PATCH", 401),
        ("PUT", 401),
        ("HEAD", 401),
        ("OPTIONS", 401),
    ],
)
def test_unauthenticated_admin_compos(api_client, method, status):
    assert api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 403),
        ("POST", 403),
        ("DELETE", 403),
        ("PATCH", 403),
        ("PUT", 403),
        ("HEAD", 403),
        ("OPTIONS", 403),
    ],
)
def test_unauthorized_admin_compos(user_api_client, method, status):
    assert user_api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    "method,status",
    [
        ("GET", 200),
        ("POST", 405),
        ("DELETE", 405),
        ("PATCH", 405),
        ("PUT", 405),
        ("HEAD", 200),
        ("OPTIONS", 200),
    ],
)
def test_authenticated_admin_compos(staff_api_client, method, status):
    assert staff_api_client.generic(method, BASE_URL).status_code == status


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_admin_compos_list_response(staff_api_client, votable_compo):
    req = staff_api_client.get(BASE_URL)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": votable_compo.id,
            "event": votable_compo.event_id,
            "name": "Votable Compo",
            "description": "Test Compo should be votable!",
            "adding_end": _dt(datetime(2025, 1, 15, 6, 0, 0, tzinfo=dt_tz.utc)),
            "editing_end": _dt(datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc)),
            "compo_start": _dt(datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc)),
            "voting_start": _dt(datetime(2025, 1, 15, 11, 30, 0, tzinfo=dt_tz.utc)),
            "voting_end": _dt(datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc)),
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
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_admin_compos_detail_response(staff_api_client, votable_compo):
    req = staff_api_client.get(f"{BASE_URL}{votable_compo.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": votable_compo.id,
        "event": votable_compo.event_id,
        "name": "Votable Compo",
        "description": "Test Compo should be votable!",
        "adding_end": _dt(datetime(2025, 1, 15, 6, 0, 0, tzinfo=dt_tz.utc)),
        "editing_end": _dt(datetime(2025, 1, 15, 10, 0, 0, tzinfo=dt_tz.utc)),
        "compo_start": _dt(datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc)),
        "voting_start": _dt(datetime(2025, 1, 15, 11, 30, 0, tzinfo=dt_tz.utc)),
        "voting_end": _dt(datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc)),
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

"""Tests for API v1 public endpoint response field validation.

Each test verifies the exact structure and field values returned by
public GET endpoints, comparing against deterministic fixture data.
"""

from datetime import datetime
from datetime import timezone as dt_tz
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from tests.api.helpers import file_url

FROZEN_TIME = "2025-01-15T12:00:00Z"
_HELSINKI = ZoneInfo("Europe/Helsinki")


def _dt(utc_dt: datetime) -> str:
    """Format a UTC datetime as the serialized string DRF returns (local timezone)."""
    local = utc_dt.astimezone(_HELSINKI)
    s = local.isoformat()
    return s.replace("+00:00", "Z")


# === Event tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_events_list_response(api_client, event):
    req = api_client.get("/api/v1/events/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": event.id,
            "name": "Instanssi 2025",
            "date": "2025-01-15",
            "mainurl": "http://localhost:8000/2025/",
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_events_detail_response(api_client, event):
    req = api_client.get(f"/api/v1/events/{event.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": event.id,
        "name": "Instanssi 2025",
        "date": "2025-01-15",
        "mainurl": "http://localhost:8000/2025/",
    }


# === Competition tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competitions_list_response(api_client, competition):
    req = api_client.get("/api/v1/competitions/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": competition.id,
            "event": competition.event_id,
            "name": "Test competition",
            "description": "<p>Test competition is the <strong>awesomest</strong> ever!</p>",
            "participation_end": _dt(datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc)),
            "start": _dt(datetime(2025, 1, 15, 13, 30, 0, tzinfo=dt_tz.utc)),
            "end": _dt(datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc)),
            "score_type": "p",
            "score_sort": 0,
            "show_results": False,
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competitions_detail_response(api_client, competition):
    req = api_client.get(f"/api/v1/competitions/{competition.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": competition.id,
        "event": competition.event_id,
        "name": "Test competition",
        "description": "<p>Test competition is the <strong>awesomest</strong> ever!</p>",
        "participation_end": _dt(datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc)),
        "start": _dt(datetime(2025, 1, 15, 13, 30, 0, tzinfo=dt_tz.utc)),
        "end": _dt(datetime(2025, 1, 15, 20, 0, 0, tzinfo=dt_tz.utc)),
        "score_type": "p",
        "score_sort": 0,
        "show_results": False,
    }


# === Competition Participation tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competition_participations_no_results(api_client, competition_participation):
    """When show_results=False, score/rank/disqualified fields are None."""
    req = api_client.get("/api/v1/competition_participations/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": competition_participation.id,
            "competition": competition_participation.competition_id,
            "participant_name": "Test Participant",
            "score": None,
            "rank": None,
            "disqualified": None,
            "disqualified_reason": None,
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competition_participations_with_results(api_client, results_competition_participation):
    """When show_results=True, score/rank/disqualified fields are populated."""
    req = api_client.get("/api/v1/competition_participations/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": results_competition_participation.id,
            "competition": results_competition_participation.competition_id,
            "participant_name": "Results Participant",
            "score": "150.0 p",
            "rank": 1,
            "disqualified": False,
            "disqualified_reason": "",
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competition_participations_no_results_detail(api_client, competition_participation):
    """Detail view: when show_results=False, score/rank/disqualified fields are None."""
    req = api_client.get(f"/api/v1/competition_participations/{competition_participation.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": competition_participation.id,
        "competition": competition_participation.competition_id,
        "participant_name": "Test Participant",
        "score": None,
        "rank": None,
        "disqualified": None,
        "disqualified_reason": None,
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_competition_participations_with_results_detail(api_client, results_competition_participation):
    """Detail view: when show_results=True, score/rank/disqualified fields are populated."""
    req = api_client.get(f"/api/v1/competition_participations/{results_competition_participation.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": results_competition_participation.id,
        "competition": results_competition_participation.competition_id,
        "participant_name": "Results Participant",
        "score": "150.0 p",
        "rank": 1,
        "disqualified": False,
        "disqualified_reason": "",
    }


# === Compo tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_compos_list_response(api_client, votable_compo):
    req = api_client.get("/api/v1/compos/")
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
            "max_image_size": 6291456,
            "source_format_list": ["zip", "7z", "gz", "bz2"],
            "entry_format_list": ["zip", "7z", "gz", "bz2"],
            "image_format_list": ["png", "jpg"],
            "show_voting_results": False,
            "entry_view_type": 0,
            "is_votable": True,
            "is_imagefile_allowed": True,
            "is_imagefile_required": False,
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_compos_detail_response(api_client, votable_compo):
    req = api_client.get(f"/api/v1/compos/{votable_compo.id}/")
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
        "max_image_size": 6291456,
        "source_format_list": ["zip", "7z", "gz", "bz2"],
        "entry_format_list": ["zip", "7z", "gz", "bz2"],
        "image_format_list": ["png", "jpg"],
        "show_voting_results": False,
        "entry_view_type": 0,
        "is_votable": True,
        "is_imagefile_allowed": True,
        "is_imagefile_required": False,
    }


# === Compo Entry tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_compo_entries_list_response(api_client, votable_compo_entry):
    """Entry visible because voting has started. show_voting_results=False so rank/score are None."""
    req = api_client.get("/api/v1/compo_entries/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": votable_compo_entry.id,
            "compo": votable_compo_entry.compo_id,
            "name": "Test Entry",
            "description": "A votable test entry",
            "creator": "Test Creator",
            "platform": "Commodore 64",
            "entryfile_url": file_url(votable_compo_entry.entryfile),
            "sourcefile_url": file_url(votable_compo_entry.sourcefile),
            "imagefile_original_url": file_url(votable_compo_entry.imagefile_original),
            "imagefile_thumbnail_url": file_url(votable_compo_entry.imagefile_thumbnail),
            "imagefile_medium_url": file_url(votable_compo_entry.imagefile_medium),
            "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "disqualified": False,
            "disqualified_reason": "",
            "score": None,
            "rank": None,
            "alternate_files": [],
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_compo_entries_detail_response(api_client, votable_compo_entry):
    req = api_client.get(f"/api/v1/compo_entries/{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": votable_compo_entry.id,
        "compo": votable_compo_entry.compo_id,
        "name": "Test Entry",
        "description": "A votable test entry",
        "creator": "Test Creator",
        "platform": "Commodore 64",
        "entryfile_url": file_url(votable_compo_entry.entryfile),
        "sourcefile_url": file_url(votable_compo_entry.sourcefile),
        "imagefile_original_url": file_url(votable_compo_entry.imagefile_original),
        "imagefile_thumbnail_url": file_url(votable_compo_entry.imagefile_thumbnail),
        "imagefile_medium_url": file_url(votable_compo_entry.imagefile_medium),
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "disqualified": False,
        "disqualified_reason": "",
        "score": None,
        "rank": None,
        "alternate_files": [],
    }


# === Programme Event tests ===


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_programme_events_list_response(api_client, program_event):
    req = api_client.get("/api/v1/programme_events/")
    assert req.status_code == 200
    assert req.data == [
        {
            "id": program_event.id,
            "event": program_event.event_id,
            "start": _dt(datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc)),
            "end": _dt(datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc)),
            "description": "A test programme event",
            "title": "Test Programme Event",
            "presenters": "Test Presenter",
            "presenters_titles": "",
            "place": "Main Stage",
        }
    ]


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_programme_events_detail_response(api_client, program_event):
    req = api_client.get(f"/api/v1/programme_events/{program_event.id}/")
    assert req.status_code == 200
    assert req.data == {
        "id": program_event.id,
        "event": program_event.event_id,
        "start": _dt(datetime(2025, 1, 15, 13, 0, 0, tzinfo=dt_tz.utc)),
        "end": _dt(datetime(2025, 1, 15, 14, 0, 0, tzinfo=dt_tz.utc)),
        "description": "A test programme event",
        "title": "Test Programme Event",
        "presenters": "Test Presenter",
        "presenters_titles": "",
        "place": "Main Stage",
    }

from datetime import datetime
from datetime import timezone as dt_tz
from zoneinfo import ZoneInfo

import pytest
from freezegun import freeze_time

from Instanssi.kompomaatti.models import Entry
from tests.api.helpers import file_url

_HELSINKI = ZoneInfo("Europe/Helsinki")
FROZEN_TIME = "2025-01-15T12:00:00Z"


def _dt(utc_dt: datetime) -> str:
    """Format a UTC datetime as the serialized string DRF returns (local timezone)."""
    local = utc_dt.astimezone(_HELSINKI)
    s = local.isoformat()
    return s.replace("+00:00", "Z")


@pytest.mark.django_db
def test_auth_events(auth_client):
    url = "/api/v1/events/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competitions(auth_client):
    url = "/api/v1/competitions/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_competition_participations(auth_client):
    url = "/api/v1/competition_participations/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_competition_participation_ok(auth_client, competition):
    url = "/api/v1/user_participations/"
    req = auth_client.post(
        url,
        data={
            "competition": competition.id,
            "participant_name": "Pertti Partisipantti",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "competition": competition.id,
        "participant_name": "Pertti Partisipantti",
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_competition_participation_fail(auth_client, competition_participation, competition):
    url = "/api/v1/user_participations/"

    # Try to make an overlapping participation, should fail
    req = auth_client.post(
        url,
        data={
            "competition": competition.id,
            "participant_name": competition_participation.participant_name,
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Olet jo osallistunut tähän kilpailuun"]}


@pytest.mark.django_db
def test_auth_competition_participation_get(auth_client, competition_participation):
    url = "/api/v1/user_participations/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": competition_participation.id,
            "competition": competition_participation.competition_id,
            "participant_name": competition_participation.participant_name,
        }
    ]


@pytest.mark.django_db
def test_auth_competition_participation_options(auth_client):
    url = "/api/v1/user_participations/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_competition_participation_instance_patch(auth_client, competition_participation):
    instance_url = "/api/v1/user_participations/{}/".format(competition_participation.id)
    req = auth_client.patch(
        instance_url,
        data={
            "id": competition_participation.id + 1,  # Should not affect anything
            "participant_name": "Pertti Perusjuntti",  # Should change
        },
    )
    assert req.status_code == 200
    assert req.data == {
        "id": competition_participation.id,
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Perusjuntti",
    }

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "id": competition_participation.id,
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Perusjuntti",
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_competition_participation_instance_put(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    req = auth_client.put(
        instance_url,
        data={
            "competition": competition_participation.competition.id,
            "participant_name": "Pertti Partisipantti",
        },
    )
    assert req.status_code == 200
    assert req.data == {
        "id": competition_participation.id,
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Partisipantti",
    }

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "id": competition_participation.id,
        "competition": competition_participation.competition_id,
        "participant_name": "Pertti Partisipantti",
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_competition_participation_instance_delete(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_auth_competition_participation_instance_options(auth_client, competition_participation):
    instance_url = f"/api/v1/user_participations/{competition_participation.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_compos(auth_client):
    url = "/api/v1/compos/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_compo_entries(auth_client):
    url = "/api/v1/compo_entries/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_post(auth_client, open_compo, entry_zip, source_zip, image_png):
    url = "/api/v1/user_entries/"
    req = auth_client.post(
        url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Awesome test entry description",
            "creator": "Test Creator 2000",
            "platform": "Linux",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201
    entry = Entry.objects.get(id=req.data["id"])
    assert req.data == {
        "id": entry.id,
        "compo": open_compo.id,
        "name": "Test Entry",
        "description": "Awesome test entry description",
        "creator": "Test Creator 2000",
        "platform": "Linux",
        "entryfile_url": file_url(entry.entryfile),
        "sourcefile_url": file_url(entry.sourcefile),
        "imagefile_original_url": file_url(entry.imagefile_original),
        "imagefile_thumbnail_url": file_url(entry.imagefile_thumbnail),
        "imagefile_medium_url": file_url(entry.imagefile_medium),
        "disqualified": False,
        "disqualified_reason": "",
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_post_uppercase_ext(auth_client, open_compo, entry_zip, source_zip, image_png):
    url = "/api/v1/user_entries/"
    entry_zip.name = "entry_file.ZIP"  # UPPERCASE EXTS
    source_zip.name = "source_file.ZIP"
    image_png.name = "image.PNG"
    req = auth_client.post(
        url,
        format="multipart",
        data={
            "compo": open_compo.id,
            "name": "Test Entry",
            "description": "Potentially problematic test entry",
            "creator": "8.3 For Life",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
            "sourcefile": source_zip,
        },
    )
    assert req.status_code == 201


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_get(auth_client, editable_compo_entry):
    url = "/api/v1/user_entries/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": editable_compo_entry.id,
            "compo": editable_compo_entry.compo_id,
            "name": editable_compo_entry.name,
            "description": editable_compo_entry.description,
            "creator": editable_compo_entry.creator,
            "platform": editable_compo_entry.platform,
            "entryfile_url": file_url(editable_compo_entry.entryfile),
            "sourcefile_url": file_url(editable_compo_entry.sourcefile),
            "imagefile_original_url": file_url(editable_compo_entry.imagefile_original),
            "imagefile_thumbnail_url": file_url(editable_compo_entry.imagefile_thumbnail),
            "imagefile_medium_url": file_url(editable_compo_entry.imagefile_medium),
            "disqualified": False,
            "disqualified_reason": "",
        }
    ]


@pytest.mark.django_db
def test_auth_user_entries_options(auth_client):
    url = "/api/v1/user_entries/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_instance_patch(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
    req = auth_client.patch(
        instance_url,
        format="multipart",
        data={
            "id": 3,  # Should not change
            "name": "Test Entry 2",  # Should change
            "description": "Awesome test entry description 2",  # Should change
            "creator": "Test Creator 3000",  # Should change
            "imagefile_original": "",
        },
    )
    assert req.status_code == 200
    entry = Entry.objects.get(id=editable_compo_entry.id)
    expected = {
        "id": editable_compo_entry.id,
        "compo": editable_compo_entry.compo_id,
        "name": "Test Entry 2",
        "description": "Awesome test entry description 2",
        "creator": "Test Creator 3000",
        "platform": editable_compo_entry.platform,
        "entryfile_url": file_url(entry.entryfile),
        "sourcefile_url": file_url(entry.sourcefile),
        "imagefile_original_url": None,
        "imagefile_thumbnail_url": None,
        "imagefile_medium_url": None,
        "disqualified": False,
        "disqualified_reason": "",
    }
    assert req.data == expected

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == expected


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_instance_put(
    auth_client, editable_compo_entry, entry_zip2, source_zip2, image_png2
):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"

    req = auth_client.put(
        instance_url,
        format="multipart",
        data={
            "compo": editable_compo_entry.compo_id,
            "name": "Test Entry",
            "description": "Awesome test entry description",
            "creator": "Test Creator 3000",
            "platform": "Linux (Ubuntu 18.04)",
            "entryfile": entry_zip2,
            "imagefile_original": image_png2,
            "sourcefile": source_zip2,
        },
    )
    assert req.status_code == 200
    entry = Entry.objects.get(id=editable_compo_entry.id)
    expected = {
        "id": editable_compo_entry.id,
        "compo": editable_compo_entry.compo_id,
        "name": "Test Entry",
        "description": "Awesome test entry description",
        "creator": "Test Creator 3000",
        "platform": "Linux (Ubuntu 18.04)",
        "entryfile_url": file_url(entry.entryfile),
        "sourcefile_url": file_url(entry.sourcefile),
        "imagefile_original_url": file_url(entry.imagefile_original),
        "imagefile_thumbnail_url": file_url(entry.imagefile_thumbnail),
        "imagefile_medium_url": file_url(entry.imagefile_medium),
        "disqualified": False,
        "disqualified_reason": "",
    }
    assert req.data == expected

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == expected


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_instance_delete(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
    assert auth_client.delete(instance_url).status_code == 204
    assert auth_client.get(instance_url).status_code == 404


@pytest.mark.django_db
def test_auth_user_entries_instance_options(auth_client, editable_compo_entry):
    instance_url = f"/api/v1/user_entries/{editable_compo_entry.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
def test_auth_programme_events(auth_client):
    url = "/api/v1/programme_events/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_store_items(auth_client):
    url = "/api/v1/store_items/"
    assert auth_client.get(url).status_code == 200
    assert auth_client.post(url).status_code == 403  # Unauthorized by permission class
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_store_transaction(auth_client):
    url = "/api/v1/store_transaction/"
    assert auth_client.get(url).status_code == 405
    assert auth_client.post(url).status_code == 400
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_current_user(auth_client, base_user):
    url = "/api/v1/current_user/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == {
        "id": base_user.id,
        "first_name": base_user.first_name,
        "last_name": base_user.last_name,
        "email": base_user.email,
    }
    assert auth_client.post(url).status_code == 405
    assert auth_client.put(url, data={}).status_code == 405
    assert auth_client.patch(url, data={}).status_code == 405
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_code_post(auth_client, event, transaction_item_a):
    url = "/api/v1/user_vote_codes/"
    req = auth_client.post(url, data={"event": event.id, "ticket_key": transaction_item_a.key})
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "time": _dt(datetime(2025, 1, 15, 12, 0, 0, tzinfo=dt_tz.utc)),
        "ticket_key": transaction_item_a.key,
    }


@pytest.mark.django_db
def test_auth_user_vote_code_post_duplicate(auth_client, ticket_vote_code):
    url = "/api/v1/user_vote_codes/"

    # Duplicate, should fail
    req = auth_client.post(
        url, data={"event": ticket_vote_code.event.id, "ticket_key": ticket_vote_code.ticket.key}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestyskoodi on jo hankittu"]}


@pytest.mark.django_db
def test_auth_user_vote_code_get(auth_client, ticket_vote_code):
    url = "/api/v1/user_vote_codes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {
            "id": ticket_vote_code.id,
            "event": ticket_vote_code.event_id,
            "time": ticket_vote_code.time,
            "ticket_key": ticket_vote_code.ticket.key,
        }
    ]


@pytest.mark.django_db
def test_auth_user_vote_code_instance(auth_client, ticket_vote_code):
    # Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)
    instance_url = f"/api/v1/user_vote_codes/{ticket_vote_code.id}/"
    assert auth_client.put(instance_url, data={}).status_code == 405
    assert auth_client.delete(instance_url).status_code == 405
    assert auth_client.patch(instance_url, data={}).status_code == 405
    assert auth_client.options(instance_url).status_code == 200

    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "id": ticket_vote_code.id,
        "event": ticket_vote_code.event_id,
        "time": ticket_vote_code.time,
        "ticket_key": ticket_vote_code.ticket.key,
    }


@pytest.mark.django_db
def test_auth_user_vote_code_request_post(auth_client, event):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.post(
        url,
        data={
            "event": event.id,
            "text": "Test request",
        },
    )
    assert req.status_code == 201
    assert req.data == {
        "id": req.data["id"],
        "event": event.id,
        "text": "Test request",
        "status": 0,
    }


@pytest.mark.django_db
def test_auth_user_vote_code_request_post_duplicate(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.post(
        url,
        data={
            "event": vote_code_request.event_id,
            "text": "Test request",
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestyskoodipyyntö on jo olemassa"]}


@pytest.mark.django_db
def test_auth_user_vote_code_request_get(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [
        {"id": 1, "event": vote_code_request.event_id, "text": "gief vote code plsthx", "status": 0}
    ]


@pytest.mark.django_db
def test_auth_user_vote_code_request_options(auth_client, vote_code_request):
    url = "/api/v1/user_vote_code_requests/"
    assert auth_client.options(url).status_code == 200


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_patch(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    req = auth_client.patch(
        instance_url,
        data={
            "id": 2,  # Should not change
            "text": "Test request 2",  # Should change
        },
    )
    assert req.status_code == 200
    expected = {
        "id": vote_code_request.id,
        "event": vote_code_request.event_id,
        "text": "Test request 2",
        "status": 0,
    }
    assert req.data == expected

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == expected


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_put(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    req = auth_client.put(
        instance_url,
        data={
            "event": vote_code_request.event_id,
            "text": "Test request",
        },
    )
    assert req.status_code == 200
    expected = {
        "id": vote_code_request.id,
        "event": vote_code_request.event_id,
        "text": "Test request",
        "status": 0,
    }
    assert req.data == expected

    # Make sure entry changed via GET as well
    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == expected


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_delete(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    assert auth_client.delete(instance_url).status_code == 405  # No delete for this


@pytest.mark.django_db
def test_auth_user_vote_code_request_instance_options(auth_client, vote_code_request):
    instance_url = f"/api/v1/user_vote_code_requests/{vote_code_request.id}/"
    assert auth_client.options(instance_url).status_code == 200


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_not_started(auth_client, editable_compo_entry):
    """This should fail due to compo voting not started"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": editable_compo_entry.compo_id, "entries": [editable_compo_entry.id]}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Kompon äänestysaika ei ole voimassa"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_missing_rights(auth_client, votable_compo_entry):
    """this should fail due to missing vote rights"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Äänestysoikeus puuttuu"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_ok(auth_client, votable_compo_entry, ticket_vote_code):
    """this should succeed, as voting is open and we have voting rights"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 201
    assert req.data == {
        "compo": votable_compo_entry.compo_id,
        "entries": [votable_compo_entry.id],
    }


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_duplicate_ok(auth_client, votable_compo_entry, ticket_vote_code, entry_vote):
    """duplicate attempt should also succeed"""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": votable_compo_entry.compo_id, "entries": [votable_compo_entry.id]}
    )
    assert req.status_code == 201


@pytest.mark.django_db
def test_auth_user_vote_get(auth_client, entry_vote):
    url = "/api/v1/user_votes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert req.data == [{"compo": entry_vote.entry.compo_id, "entries": [entry_vote.entry.id]}]


@pytest.mark.django_db
def test_auth_user_vote_instance(auth_client, entry_vote_group):
    """Test instance stuff. DELETE, PUT, PATCH = 405 (methods not implemented)"""
    instance_url = f"/api/v1/user_votes/{entry_vote_group.id}/"
    assert auth_client.put(instance_url, data={}).status_code == 405
    assert auth_client.delete(instance_url).status_code == 405
    assert auth_client.patch(instance_url, data={}).status_code == 405
    assert auth_client.options(instance_url).status_code == 200

    req = auth_client.get(instance_url)
    assert req.status_code == 200
    assert req.data == {
        "compo": entry_vote_group.compo_id,
        "entries": [],
    }


# --- User data isolation tests ---


@pytest.mark.django_db
def test_auth_user_entries_cannot_see_other_users_entries(
    auth_client, editable_compo_entry, other_user_entry
):
    """Authenticated user should only see their own entries, not another user's."""
    url = "/api/v1/user_entries/"
    req = auth_client.get(url)
    assert req.status_code == 200
    ids = [e["id"] for e in req.data]
    assert editable_compo_entry.id in ids
    assert other_user_entry.id not in ids


@pytest.mark.django_db
def test_auth_user_participations_cannot_see_other_users(
    auth_client, competition_participation, normal_user_competition_participation
):
    """Authenticated user should only see their own participations."""
    url = "/api/v1/user_participations/"
    req = auth_client.get(url)
    assert req.status_code == 200
    ids = [p["id"] for p in req.data]
    assert competition_participation.id in ids
    assert normal_user_competition_participation.id not in ids


@pytest.mark.django_db
def test_auth_user_vote_codes_cannot_see_other_users(
    auth_client, ticket_vote_code, other_user_ticket_vote_code
):
    """Authenticated user should only see their own vote codes."""
    url = "/api/v1/user_vote_codes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    ids = [vc["id"] for vc in req.data]
    assert ticket_vote_code.id in ids
    assert other_user_ticket_vote_code.id not in ids


@pytest.mark.django_db
def test_auth_user_votes_cannot_see_other_users(auth_client, entry_vote_group, other_user_vote_group):
    """Authenticated user should only see their own vote groups."""
    url = "/api/v1/user_votes/"
    req = auth_client.get(url)
    assert req.status_code == 200
    assert len(req.data) == 1
    assert req.data[0]["compo"] == entry_vote_group.compo_id


@pytest.mark.django_db
def test_auth_user_vote_code_requests_cannot_see_other_users(
    auth_client, vote_code_request, other_user_vote_code_request
):
    """Authenticated user should only see their own vote code requests."""
    url = "/api/v1/user_vote_code_requests/"
    req = auth_client.get(url)
    assert req.status_code == 200
    ids = [r["id"] for r in req.data]
    assert vote_code_request.id in ids
    assert other_user_vote_code_request.id not in ids


# --- Time-window validation tests ---


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_voting_ended(auth_client, closed_compo_entry, ticket_vote_code):
    """Voting after the voting window closes should fail."""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url, data={"compo": closed_compo_entry.compo_id, "entries": [closed_compo_entry.id]}
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Kompon äänestysaika ei ole voimassa"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_post_fail_adding_closed(auth_client, votable_compo, entry_zip, image_png):
    """Submitting an entry after adding_end should fail."""
    url = "/api/v1/user_entries/"
    req = auth_client.post(
        url,
        format="multipart",
        data={
            "compo": votable_compo.id,
            "name": "Late Entry",
            "description": "Too late",
            "creator": "Late Creator",
            "entryfile": entry_zip,
            "imagefile_original": image_png,
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Kompon lisäysaika on päättynyt"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_delete_fail_editing_closed(auth_client, closed_compo_entry):
    """Deleting an entry after editing_end should fail."""
    instance_url = f"/api/v1/user_entries/{closed_compo_entry.id}/"
    req = auth_client.delete(instance_url)
    assert req.status_code == 400


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_entries_put_fail_editing_closed(auth_client, closed_compo_entry, entry_zip2, image_png2):
    """Updating an entry after editing_end should fail."""
    instance_url = f"/api/v1/user_entries/{closed_compo_entry.id}/"
    req = auth_client.put(
        instance_url,
        format="multipart",
        data={
            "compo": closed_compo_entry.compo_id,
            "name": "Updated Entry",
            "description": "Updated desc",
            "creator": "Updated Creator",
            "entryfile": entry_zip2,
            "imagefile_original": image_png2,
        },
    )
    assert req.status_code == 400
    assert req.data == {"non_field_errors": ["Kompon muokkausaika on päättynyt"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_participation_delete_fail_closed(auth_client, started_competition_participation):
    """Deleting participation after participation_end should fail."""
    instance_url = f"/api/v1/user_participations/{started_competition_participation.id}/"
    req = auth_client.delete(instance_url)
    assert req.status_code == 400


# --- Vote code validation edge cases ---


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_code_post_unpaid_ticket(auth_client, event, unpaid_ticket):
    """Claiming an unpaid ticket should fail."""
    url = "/api/v1/user_vote_codes/"
    req = auth_client.post(url, data={"event": event.id, "ticket_key": unpaid_ticket.key})
    assert req.status_code == 400
    assert req.data == {"ticket_key": ["Pyydettyä lippuavainta ei ole olemassa!"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_code_post_non_ticket_item(auth_client, event, non_ticket_transaction_item):
    """Claiming a non-ticket item should fail."""
    url = "/api/v1/user_vote_codes/"
    req = auth_client.post(url, data={"event": event.id, "ticket_key": non_ticket_transaction_item.key})
    assert req.status_code == 400
    assert req.data == {"ticket_key": ["Pyydettyä lippuavainta ei ole olemassa!"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_code_post_nonexistent_key(auth_client, event):
    """Claiming a completely bogus ticket key should fail."""
    url = "/api/v1/user_vote_codes/"
    req = auth_client.post(url, data={"event": event.id, "ticket_key": "zzzzzzzzzzzzzzzz"})
    assert req.status_code == 400
    assert req.data == {"ticket_key": ["Pyydettyä lippuavainta ei ole olemassa!"]}


# --- Vote validation edge cases ---


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_duplicate_entries(auth_client, votable_compo_entry, ticket_vote_code):
    """Voting for the same entry twice should fail."""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url,
        data={
            "compo": votable_compo_entry.compo_id,
            "entries": [votable_compo_entry.id, votable_compo_entry.id],
        },
    )
    assert req.status_code == 400
    assert req.data == {"entries": ["Voit äänestää entryä vain kerran"]}


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_wrong_compo_entry(
    auth_client, votable_compo, editable_compo_entry, ticket_vote_code
):
    """Voting for an entry from a different compo should fail."""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url,
        data={
            "compo": votable_compo.id,
            "entries": [editable_compo_entry.id],
        },
    )
    assert req.status_code == 400
    assert "entries" in req.data


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_auth_user_vote_post_fail_disqualified_entry(
    auth_client, votable_compo, disqualified_entry, ticket_vote_code
):
    """Voting for a disqualified entry should fail (filtered by queryset)."""
    url = "/api/v1/user_votes/"
    req = auth_client.post(
        url,
        data={
            "compo": votable_compo.id,
            "entries": [disqualified_entry.id],
        },
    )
    assert req.status_code == 400

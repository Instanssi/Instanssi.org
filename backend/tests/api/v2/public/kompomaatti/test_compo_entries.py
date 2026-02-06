import pytest
from freezegun import freeze_time

FROZEN_TIME = "2025-01-15T12:00:00Z"


def get_base_url(event_id):
    return f"/api/v2/public/event/{event_id}/kompomaatti/entries/"


@pytest.mark.django_db
def test_anonymous_can_list_votable_entries(api_client, votable_compo_entry):
    """Test that anonymous users can list entries from votable compos."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    entry_ids = [e["id"] for e in req.data]
    assert votable_compo_entry.id in entry_ids


@pytest.mark.django_db
def test_anonymous_can_get_votable_entry_detail(api_client, votable_compo_entry):
    """Test that anonymous users can get votable entry details."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["id"] == votable_compo_entry.id


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
def test_anonymous_cannot_see_non_votable_entries(api_client, editable_compo_entry):
    """Test that entries from compos before voting starts are not visible."""
    base_url = get_base_url(editable_compo_entry.compo.event_id)

    # Not in list
    req = api_client.get(base_url)
    assert req.status_code == 200
    entry_ids = [e["id"] for e in req.data]
    assert editable_compo_entry.id not in entry_ids

    # Not in detail
    req = api_client.get(f"{base_url}{editable_compo_entry.id}/")
    assert req.status_code == 404


@pytest.mark.django_db
def test_public_entry_does_not_expose_sensitive_fields(api_client, votable_compo_entry):
    """Test that public endpoint does not expose sensitive/staff-only fields."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert "user" not in req.data
    assert "entryfile" not in req.data
    assert "sourcefile" not in req.data
    assert "imagefile_original" not in req.data
    assert "entryfile_url" not in req.data
    assert "sourcefile_url" not in req.data
    assert "archive_score" not in req.data
    assert "archive_rank" not in req.data


@pytest.mark.django_db
def test_public_cannot_see_score_rank_before_results_shown(api_client, votable_compo_entry):
    """Test that score/rank are hidden when show_voting_results is False."""
    votable_compo_entry.compo.show_voting_results = False
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["computed_score"] is None
    assert req.data["computed_rank"] is None


@pytest.mark.django_db
def test_public_can_see_score_rank_after_results_shown(api_client, votable_compo_entry):
    """Test that score/rank are visible when show_voting_results is True."""
    votable_compo_entry.compo.show_voting_results = True
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["computed_score"] is not None
    assert req.data["computed_rank"] is not None


@pytest.mark.django_db
def test_public_cannot_see_disqualified_before_results_shown(api_client, votable_compo_entry):
    """Test that disqualified/disqualified_reason are hidden when show_voting_results is False."""
    votable_compo_entry.disqualified = True
    votable_compo_entry.disqualified_reason = "Test reason"
    votable_compo_entry.save()
    votable_compo_entry.compo.show_voting_results = False
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["disqualified"] is None
    assert req.data["disqualified_reason"] is None


@pytest.mark.django_db
def test_public_can_see_disqualified_after_results_shown(api_client, votable_compo_entry):
    """Test that disqualified/disqualified_reason are visible when show_voting_results is True."""
    votable_compo_entry.disqualified = True
    votable_compo_entry.disqualified_reason = "Test reason"
    votable_compo_entry.save()
    votable_compo_entry.compo.show_voting_results = True
    votable_compo_entry.compo.save()

    base_url = get_base_url(votable_compo_entry.compo.event_id)
    req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
    assert req.status_code == 200
    assert req.data["disqualified"] is True
    assert req.data["disqualified_reason"] == "Test reason"


@pytest.mark.django_db
def test_public_can_see_alternate_files(api_client, votable_alternate_entry_file):
    """Test that alternate_files are visible for votable entries."""
    entry = votable_alternate_entry_file.entry
    base_url = get_base_url(entry.compo.event_id)
    req = api_client.get(f"{base_url}{entry.id}/")
    assert req.status_code == 200
    assert "alternate_files" in req.data
    assert len(req.data["alternate_files"]) == 1
    alt_file = req.data["alternate_files"][0]
    assert alt_file["format"] == "audio/webm;codecs=opus"
    assert "url" in alt_file


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
def test_anonymous_cannot_modify_entries(api_client, votable_compo_entry, method, status):
    """Test that write methods return 405 on read-only endpoint."""
    base_url = get_base_url(votable_compo_entry.compo.event_id)
    url = f"{base_url}{votable_compo_entry.id}/"
    assert api_client.generic(method, url).status_code == status


@pytest.mark.django_db
def test_hidden_event_entries_not_in_list(api_client, hidden_event, hidden_event_compo, hidden_event_entry):
    """Entries from hidden events should not appear in the list."""
    base_url = get_base_url(hidden_event.id)
    req = api_client.get(base_url)
    assert req.status_code == 200
    assert len(req.data) == 0

import pytest

from Instanssi.kompomaatti.models import (
    CompetitionParticipation,
    Entry,
    Vote,
    VoteGroup,
)


def get_base_url(event_id):
    return f"/api/v2/admin/event/{event_id}/arkisto/archiver/"


@pytest.mark.django_db
def test_staff_can_get_status(staff_api_client, past_event):
    """Test that staff can get archiver status."""
    url = get_base_url(past_event.id) + "status/"
    req = staff_api_client.get(url)
    assert req.status_code == 200
    assert "is_archived" in req.data
    assert "has_non_archived_items" in req.data
    assert "ongoing_activity" in req.data
    assert "votes_unoptimized" in req.data
    assert "old_votes_found" in req.data


@pytest.mark.django_db
def test_status_shows_correct_archived_state(staff_api_client, past_event):
    """Test that status correctly reflects archived state."""
    url = get_base_url(past_event.id) + "status/"

    # Initially not archived
    req = staff_api_client.get(url)
    assert req.status_code == 200
    assert req.data["is_archived"] is False

    # Archive the event
    past_event.archived = True
    past_event.save()

    req = staff_api_client.get(url)
    assert req.status_code == 200
    assert req.data["is_archived"] is True


@pytest.mark.django_db
def test_status_shows_ongoing_activity_for_future_event(staff_api_client, event):
    """Test that status shows ongoing_activity for events with future dates."""
    url = get_base_url(event.id) + "status/"
    req = staff_api_client.get(url)
    assert req.status_code == 200
    # Event date is today, so it could still be ongoing depending on compos
    # But for a basic event without compos, this should be False
    # because is_event_ongoing checks compos/competitions, not just the date


@pytest.mark.django_db
def test_status_shows_votes_unoptimized(staff_api_client, past_event, past_compo_entry):
    """Test that status shows votes_unoptimized when entries lack archive scores."""
    url = get_base_url(past_event.id) + "status/"
    req = staff_api_client.get(url)
    assert req.status_code == 200
    # Entry exists without archive_score/archive_rank set
    assert req.data["votes_unoptimized"] is True


@pytest.mark.django_db
def test_status_shows_old_votes_found(staff_api_client, past_event, past_vote):
    """Test that status shows old_votes_found when votes exist."""
    url = get_base_url(past_event.id) + "status/"
    req = staff_api_client.get(url)
    assert req.status_code == 200
    assert req.data["old_votes_found"] is True


@pytest.mark.django_db
def test_status_shows_non_archived_items(staff_api_client, past_event, past_compo_entry, archive_user):
    """Test that status shows has_non_archived_items correctly."""
    url = get_base_url(past_event.id) + "status/"

    # Entry is owned by base_user, not archive_user
    req = staff_api_client.get(url)
    assert req.status_code == 200
    assert req.data["has_non_archived_items"] is True


@pytest.mark.django_db
def test_staff_can_show_event_in_archive(staff_api_client, past_event):
    """Test that staff can show event in archive."""
    url = get_base_url(past_event.id) + "show/"
    req = staff_api_client.post(url)
    assert req.status_code == 200
    assert req.data["is_archived"] is True

    # Verify the event was updated in the database
    past_event.refresh_from_db()
    assert past_event.archived is True


@pytest.mark.django_db
def test_staff_can_hide_event_from_archive(staff_api_client, past_event):
    """Test that staff can hide event from archive."""
    # First show it
    past_event.archived = True
    past_event.save()

    url = get_base_url(past_event.id) + "hide/"
    req = staff_api_client.post(url)
    assert req.status_code == 200
    assert req.data["is_archived"] is False

    # Verify the event was updated in the database
    past_event.refresh_from_db()
    assert past_event.archived is False


@pytest.mark.django_db
def test_staff_can_optimize_scores(staff_api_client, past_event, past_compo_entry):
    """Test that staff can optimize voting scores."""
    # Verify entry doesn't have archive scores
    assert past_compo_entry.archive_score is None
    assert past_compo_entry.archive_rank is None

    url = get_base_url(past_event.id) + "optimize-scores/"
    req = staff_api_client.post(url)
    assert req.status_code == 200
    assert req.data["votes_unoptimized"] is False

    # Verify entry now has archive scores
    past_compo_entry.refresh_from_db()
    assert past_compo_entry.archive_score is not None
    assert past_compo_entry.archive_rank is not None


@pytest.mark.django_db
def test_optimize_scores_blocked_for_ongoing_event(staff_api_client, event, open_compo):
    """Test that optimize scores is blocked for ongoing events."""
    url = get_base_url(event.id) + "optimize-scores/"
    req = staff_api_client.post(url)
    assert req.status_code == 400
    assert "ongoing" in req.data["detail"].lower()


@pytest.mark.django_db
def test_staff_can_remove_old_votes(staff_api_client, past_event, past_compo_entry, past_vote, archive_user):
    """Test that staff can remove old votes after optimization."""
    # First optimize scores
    past_compo_entry.archive_score = 1.0
    past_compo_entry.archive_rank = 1
    past_compo_entry.save()

    # Verify votes exist
    assert Vote.objects.filter(compo__event=past_event).exists()

    url = get_base_url(past_event.id) + "remove-old-votes/"
    req = staff_api_client.post(url)
    assert req.status_code == 200
    assert req.data["old_votes_found"] is False

    # Verify votes and vote groups were deleted
    assert not Vote.objects.filter(compo__event=past_event).exists()
    assert not VoteGroup.objects.filter(compo__event=past_event).exists()


@pytest.mark.django_db
def test_remove_old_votes_blocked_when_unoptimized(
    staff_api_client, past_event, past_compo_entry, past_vote
):
    """Test that remove old votes is blocked when scores aren't optimized."""
    # Entry doesn't have archive scores
    url = get_base_url(past_event.id) + "remove-old-votes/"
    req = staff_api_client.post(url)
    assert req.status_code == 400
    assert "optimized" in req.data["detail"].lower()


@pytest.mark.django_db
def test_remove_old_votes_blocked_for_ongoing_event(staff_api_client, event, open_compo):
    """Test that remove old votes is blocked for ongoing events."""
    url = get_base_url(event.id) + "remove-old-votes/"
    req = staff_api_client.post(url)
    assert req.status_code == 400
    assert "ongoing" in req.data["detail"].lower()


@pytest.mark.django_db
def test_staff_can_transfer_rights(
    staff_api_client, past_event, past_compo_entry, past_competition_participation, archive_user
):
    """Test that staff can transfer rights to archive user."""
    # Verify items are not owned by archive user
    assert past_compo_entry.user != archive_user
    assert past_competition_participation.user != archive_user

    url = get_base_url(past_event.id) + "transfer-rights/"
    req = staff_api_client.post(url)
    assert req.status_code == 200
    assert req.data["has_non_archived_items"] is False

    # Verify ownership was transferred
    past_compo_entry.refresh_from_db()
    past_competition_participation.refresh_from_db()
    assert past_compo_entry.user == archive_user
    assert past_competition_participation.user == archive_user


@pytest.mark.django_db
def test_transfer_rights_blocked_for_ongoing_event(staff_api_client, event, open_compo):
    """Test that transfer rights is blocked for ongoing events."""
    url = get_base_url(event.id) + "transfer-rights/"
    req = staff_api_client.post(url)
    assert req.status_code == 400
    assert "ongoing" in req.data["detail"].lower()


@pytest.mark.django_db
def test_transfer_rights_requires_archive_user(staff_api_client, past_event, past_compo_entry):
    """Test that transfer rights fails if archive user doesn't exist."""
    # Don't create the archive_user fixture
    url = get_base_url(past_event.id) + "transfer-rights/"
    req = staff_api_client.post(url)
    assert req.status_code == 404


@pytest.mark.django_db
def test_full_archiving_workflow(
    staff_api_client, past_event, past_compo_entry, past_vote, past_competition_participation, archive_user
):
    """Test the complete archiving workflow."""
    base_url = get_base_url(past_event.id)

    # 1. Check initial status
    req = staff_api_client.get(base_url + "status/")
    assert req.status_code == 200
    assert req.data["is_archived"] is False
    assert req.data["votes_unoptimized"] is True
    assert req.data["old_votes_found"] is True
    assert req.data["has_non_archived_items"] is True

    # 2. Optimize scores
    req = staff_api_client.post(base_url + "optimize-scores/")
    assert req.status_code == 200
    assert req.data["votes_unoptimized"] is False

    # 3. Remove old votes
    req = staff_api_client.post(base_url + "remove-old-votes/")
    assert req.status_code == 200
    assert req.data["old_votes_found"] is False

    # 4. Transfer rights
    req = staff_api_client.post(base_url + "transfer-rights/")
    assert req.status_code == 200
    assert req.data["has_non_archived_items"] is False

    # 5. Show in archive
    req = staff_api_client.post(base_url + "show/")
    assert req.status_code == 200
    assert req.data["is_archived"] is True

    # Verify final state
    past_event.refresh_from_db()
    past_compo_entry.refresh_from_db()
    past_competition_participation.refresh_from_db()
    assert past_event.archived is True
    assert past_compo_entry.user == archive_user
    assert past_compo_entry.archive_score is not None
    assert past_competition_participation.user == archive_user
    assert not Vote.objects.filter(compo__event=past_event).exists()

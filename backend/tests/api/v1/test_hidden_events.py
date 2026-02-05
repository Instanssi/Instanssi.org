"""Tests for hidden event filtering in API v1 endpoints."""

import pytest
from freezegun import freeze_time

from Instanssi.kompomaatti.models import (
    TicketVoteCode,
    VoteCodeRequest,
    VoteGroup,
)

FROZEN_TIME = "2025-01-15T12:00:00Z"


@pytest.fixture
def hidden_event_vote_code_request(hidden_event, base_user) -> VoteCodeRequest:
    """Vote code request for a hidden event."""
    return VoteCodeRequest.objects.create(
        event=hidden_event,
        user=base_user,
        text="Please give me voting rights",
        status=0,
    )


@pytest.fixture
def hidden_event_ticket_vote_code(hidden_event, base_user, transaction_item_a) -> TicketVoteCode:
    """Ticket vote code for a hidden event."""
    return TicketVoteCode.objects.create(
        event=hidden_event,
        ticket=transaction_item_a,
        associated_to=base_user,
    )


@pytest.fixture
def hidden_event_vote_group(base_user, hidden_event_compo) -> VoteGroup:
    """Vote group for a hidden event's compo."""
    return VoteGroup.objects.create(
        user=base_user,
        compo=hidden_event_compo,
    )


# === Public API Tests ===


@pytest.mark.django_db
class TestEventsHidden:
    """Tests for hidden events in events API."""

    def test_hidden_event_not_in_list(self, api_client, event, hidden_event):
        """Hidden events should not appear in the events list."""
        req = api_client.get("/api/v1/events/")
        assert req.status_code == 200
        event_ids = [e["id"] for e in req.data]
        assert event.id in event_ids
        assert hidden_event.id not in event_ids

    def test_hidden_event_detail_returns_404(self, api_client, hidden_event):
        """Hidden event detail should return 404."""
        req = api_client.get(f"/api/v1/events/{hidden_event.id}/")
        assert req.status_code == 404

    def test_visible_event_still_accessible(self, api_client, event):
        """Visible events should still be accessible."""
        req = api_client.get(f"/api/v1/events/{event.id}/")
        assert req.status_code == 200
        assert req.data["id"] == event.id


@pytest.mark.django_db
class TestComposHidden:
    """Tests for hidden event compos in API."""

    def test_hidden_event_compos_not_in_list(self, api_client, open_compo, hidden_event_compo):
        """Compos from hidden events should not appear in the list."""
        req = api_client.get("/api/v1/compos/")
        assert req.status_code == 200
        compo_ids = [c["id"] for c in req.data]
        assert open_compo.id in compo_ids
        assert hidden_event_compo.id not in compo_ids

    def test_hidden_event_compo_detail_returns_404(self, api_client, hidden_event_compo):
        """Compo detail from hidden event should return 404."""
        req = api_client.get(f"/api/v1/compos/{hidden_event_compo.id}/")
        assert req.status_code == 404


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestCompoEntriesHidden:
    """Tests for hidden event entries in API."""

    def test_hidden_event_entries_not_in_list(self, api_client, votable_compo_entry, hidden_event_entry):
        """Entries from hidden events should not appear in the list."""
        req = api_client.get("/api/v1/compo_entries/")
        assert req.status_code == 200
        entry_ids = [e["id"] for e in req.data]
        assert hidden_event_entry.id not in entry_ids


@pytest.mark.django_db
class TestCompetitionsHidden:
    """Tests for hidden event competitions in API."""

    def test_hidden_event_competitions_not_in_list(self, api_client, competition, hidden_event_competition):
        """Competitions from hidden events should not appear in the list."""
        req = api_client.get("/api/v1/competitions/")
        assert req.status_code == 200
        competition_ids = [c["id"] for c in req.data]
        assert competition.id in competition_ids
        assert hidden_event_competition.id not in competition_ids

    def test_hidden_event_competition_detail_returns_404(self, api_client, hidden_event_competition):
        """Competition detail from hidden event should return 404."""
        req = api_client.get(f"/api/v1/competitions/{hidden_event_competition.id}/")
        assert req.status_code == 404


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestCompetitionParticipationsHidden:
    """Tests for hidden event participations in API."""

    def test_hidden_event_participations_not_in_list(
        self, api_client, started_competition_participation, hidden_event_participation
    ):
        """Participations from hidden events should not appear in the list."""
        req = api_client.get("/api/v1/competition_participations/")
        assert req.status_code == 200
        participation_ids = [p["id"] for p in req.data]
        assert started_competition_participation.id in participation_ids
        assert hidden_event_participation.id not in participation_ids


@pytest.mark.django_db
class TestProgrammeEventsHidden:
    """Tests for hidden event programme events in API."""

    def test_hidden_event_programme_not_in_list(self, api_client, program_event, hidden_event_program):
        """Programme events from hidden events should not appear in the list."""
        req = api_client.get("/api/v1/programme_events/")
        assert req.status_code == 200
        program_ids = [p["id"] for p in req.data]
        assert program_event.id in program_ids
        assert hidden_event_program.id not in program_ids

    def test_hidden_event_programme_detail_returns_404(self, api_client, hidden_event_program):
        """Programme event detail from hidden event should return 404."""
        req = api_client.get(f"/api/v1/programme_events/{hidden_event_program.id}/")
        assert req.status_code == 404


# === Authenticated User API Tests ===


@pytest.mark.django_db
class TestUserEntriesHidden:
    """Tests for hidden event user entries in API."""

    def test_user_cannot_list_entries_for_hidden_event(
        self, auth_client, hidden_event_compo, hidden_event_entry
    ):
        """User should not see their entries for hidden events."""
        req = auth_client.get("/api/v1/user_entries/")
        assert req.status_code == 200
        entry_ids = [e["id"] for e in req.data]
        assert hidden_event_entry.id not in entry_ids


@pytest.mark.django_db
class TestUserParticipationsHidden:
    """Tests for hidden event user participations in API."""

    def test_user_cannot_list_participations_for_hidden_event(
        self, auth_client, hidden_event_competition, hidden_event_participation
    ):
        """User should not see their participations for hidden events."""
        req = auth_client.get("/api/v1/user_participations/")
        assert req.status_code == 200
        participation_ids = [p["id"] for p in req.data]
        assert hidden_event_participation.id not in participation_ids


@pytest.mark.django_db
class TestUserVoteCodeRequestsHidden:
    """Tests for hidden event vote code requests in API."""

    def test_user_cannot_list_vote_code_requests_for_hidden_event(
        self, auth_client, vote_code_request, hidden_event_vote_code_request
    ):
        """User should not see their vote code requests for hidden events."""
        req = auth_client.get("/api/v1/user_vote_code_requests/")
        assert req.status_code == 200
        request_ids = [r["id"] for r in req.data]
        assert vote_code_request.id in request_ids
        assert hidden_event_vote_code_request.id not in request_ids


@pytest.mark.django_db
class TestUserVoteCodesHidden:
    """Tests for hidden event ticket vote codes in API."""

    def test_user_cannot_list_vote_codes_for_hidden_event(
        self, auth_client, ticket_vote_code, hidden_event_ticket_vote_code
    ):
        """User should not see their ticket vote codes for hidden events."""
        req = auth_client.get("/api/v1/user_vote_codes/")
        assert req.status_code == 200
        code_ids = [c["id"] for c in req.data]
        assert ticket_vote_code.id in code_ids
        assert hidden_event_ticket_vote_code.id not in code_ids


@pytest.mark.django_db
class TestUserVotesHidden:
    """Tests for hidden event vote groups in API."""

    def test_user_cannot_list_votes_for_hidden_event(
        self, auth_client, entry_vote_group, hidden_event_vote_group
    ):
        """User should not see their vote groups for hidden events."""
        req = auth_client.get("/api/v1/user_votes/")
        assert req.status_code == 200
        vote_group_ids = [v["compo"] for v in req.data]  # v1 API returns compo, not id
        assert entry_vote_group.compo_id in vote_group_ids
        assert hidden_event_vote_group.compo_id not in vote_group_ids

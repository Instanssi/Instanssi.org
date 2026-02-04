"""Tests for score and rank calculations in API v2 admin endpoints.

Admin endpoints always expose score/rank regardless of show_voting_results
or show_results settings, and also expose archive_score/archive_rank as
separate fields for compo entries.
"""

import pytest
from freezegun import freeze_time

from Instanssi.kompomaatti.models import (
    CompetitionParticipation,
    Vote,
    VoteGroup,
)

FROZEN_TIME = "2025-01-15T12:00:00Z"


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestAdminCompoEntryScoreRank:
    """Test admin compo entry score/rank values."""

    def test_vote_based_scores(
        self,
        staff_api_client,
        votable_compo,
        votable_compo_entry,
        second_votable_entry,
        base_user,
        normal_user,
    ):
        """Admin sees correct vote-calculated scores regardless of show_voting_results."""
        # User 1: entry1=1st, entry2=2nd
        g1 = VoteGroup.objects.create(user=base_user, compo=votable_compo)
        Vote.objects.create(user=base_user, compo=votable_compo, entry=votable_compo_entry, rank=1, group=g1)
        Vote.objects.create(
            user=base_user, compo=votable_compo, entry=second_votable_entry, rank=2, group=g1
        )

        # User 2: entry1=1st, entry2=1st
        g2 = VoteGroup.objects.create(user=normal_user, compo=votable_compo)
        Vote.objects.create(
            user=normal_user, compo=votable_compo, entry=votable_compo_entry, rank=1, group=g2
        )
        Vote.objects.create(
            user=normal_user, compo=votable_compo, entry=second_votable_entry, rank=1, group=g2
        )

        # entry1: 1/1 + 1/1 = 2.0, entry2: 1/2 + 1/1 = 1.5
        base_url = f"/api/v2/admin/event/{votable_compo.event_id}/kompomaatti/entries/"
        req = staff_api_client.get(base_url)
        assert req.status_code == 200
        entries = {e["name"]: e for e in req.data}

        assert entries["Test Entry"]["computed_score"] == pytest.approx(2.0)
        assert entries["Test Entry"]["computed_rank"] == 1
        assert entries["Second Entry"]["computed_score"] == pytest.approx(1.5)
        assert entries["Second Entry"]["computed_rank"] == 2

    def test_archive_score_rank_exposed_and_used(self, staff_api_client, closed_compo_entry):
        """Admin sees archive_score/archive_rank as separate fields, and they affect score/rank."""
        base_url = f"/api/v2/admin/event/{closed_compo_entry.compo.event_id}/kompomaatti/entries/"
        req = staff_api_client.get(f"{base_url}{closed_compo_entry.id}/")
        assert req.status_code == 200
        assert req.data["archive_score"] == 5.0
        assert req.data["archive_rank"] == 1
        # computed_score and computed_rank should reflect archive values
        assert req.data["computed_score"] == 5.0
        assert req.data["computed_rank"] == 1

    def test_disqualified_entry_score(self, staff_api_client, votable_compo_entry):
        """Admin sees disqualified entry score as -1."""
        votable_compo_entry.disqualified = True
        votable_compo_entry.save()

        base_url = f"/api/v2/admin/event/{votable_compo_entry.compo.event_id}/kompomaatti/entries/"
        req = staff_api_client.get(f"{base_url}{votable_compo_entry.id}/")
        assert req.status_code == 200
        assert req.data["computed_score"] == -1.0


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestAdminCompetitionParticipationScoreRank:
    """Test admin competition participation score/rank values."""

    def test_ranking_with_multiple_participants(
        self, staff_api_client, results_competition, base_user, normal_user
    ):
        """Admin sees correct ranking across multiple participants."""
        CompetitionParticipation.objects.create(
            competition=results_competition, user=base_user, participant_name="Winner", score=300.0
        )
        CompetitionParticipation.objects.create(
            competition=results_competition, user=normal_user, participant_name="Runner Up", score=100.0
        )

        base_url = (
            f"/api/v2/admin/event/{results_competition.event_id}/kompomaatti/competition_participations/"
        )
        req = staff_api_client.get(base_url)
        assert req.status_code == 200
        parts = {p["participant_name"]: p for p in req.data}

        assert parts["Winner"]["score"] == 300.0
        assert parts["Winner"]["computed_rank"] == 1
        assert parts["Runner Up"]["score"] == 100.0
        assert parts["Runner Up"]["computed_rank"] == 2

    def test_score_rank_visible_without_show_results(self, staff_api_client, competition_participation):
        """Admin sees score/rank even when show_results is False."""
        base_url = (
            f"/api/v2/admin/event/{competition_participation.competition.event_id}"
            f"/kompomaatti/competition_participations/"
        )
        req = staff_api_client.get(f"{base_url}{competition_participation.id}/")
        assert req.status_code == 200
        assert req.data["score"] == 100.0
        assert req.data["computed_rank"] == 1

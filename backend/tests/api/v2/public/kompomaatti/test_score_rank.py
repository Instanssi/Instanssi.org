"""Tests for score and rank calculations in API v2 public endpoints.

These tests validate the actual calculated score and rank values
through the v2 public API, which is critical for verifying correctness
when moving score/rank algorithms to the database side.
"""

from datetime import datetime
from datetime import timezone as dt_tz

import pytest
from freezegun import freeze_time

from Instanssi.kompomaatti.models import (
    Competition,
    CompetitionParticipation,
    Vote,
    VoteGroup,
)

FROZEN_TIME = "2025-01-15T12:00:00Z"


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestCompoEntryScoreRank:
    """Test compo entry score and rank calculations via v2 public API."""

    def test_vote_based_scores_and_ranking(
        self,
        api_client,
        votable_compo,
        votable_compo_entry,
        second_votable_entry,
        third_votable_entry,
        base_user,
        normal_user,
    ):
        """Scores are sum(1/rank) from votes; entries ranked by descending score."""
        votable_compo.show_voting_results = True
        votable_compo.save()

        # User 1: entry1=1st, entry2=2nd, entry3=3rd
        g1 = VoteGroup.objects.create(user=base_user, compo=votable_compo)
        Vote.objects.create(user=base_user, compo=votable_compo, entry=votable_compo_entry, rank=1, group=g1)
        Vote.objects.create(
            user=base_user, compo=votable_compo, entry=second_votable_entry, rank=2, group=g1
        )
        Vote.objects.create(user=base_user, compo=votable_compo, entry=third_votable_entry, rank=3, group=g1)

        # User 2: entry1=1st, entry3=2nd (no vote for entry2)
        g2 = VoteGroup.objects.create(user=normal_user, compo=votable_compo)
        Vote.objects.create(
            user=normal_user, compo=votable_compo, entry=votable_compo_entry, rank=1, group=g2
        )
        Vote.objects.create(
            user=normal_user, compo=votable_compo, entry=third_votable_entry, rank=2, group=g2
        )

        base_url = f"/api/v2/public/event/{votable_compo.event_id}/kompomaatti/entries/"
        req = api_client.get(base_url)
        assert req.status_code == 200
        entries = {e["name"]: e for e in req.data}

        assert entries["Test Entry"]["score"] == pytest.approx(2.0)
        assert entries["Test Entry"]["rank"] == 1
        assert entries["Second Entry"]["score"] == pytest.approx(0.5)
        assert entries["Second Entry"]["rank"] == 3
        assert entries["Third Entry"]["score"] == pytest.approx(1 / 3 + 1 / 2)
        assert entries["Third Entry"]["rank"] == 2

    def test_archive_score_rank_override(self, api_client, closed_compo, closed_compo_entry):
        """archive_score and archive_rank take precedence over calculated values."""
        closed_compo.show_voting_results = True
        closed_compo.save()

        base_url = f"/api/v2/public/event/{closed_compo.event_id}/kompomaatti/entries/"
        req = api_client.get(f"{base_url}{closed_compo_entry.id}/")
        assert req.status_code == 200
        assert req.data["score"] == 5.0
        assert req.data["rank"] == 1

    def test_disqualified_entry_score(self, api_client, votable_compo, votable_compo_entry):
        """Disqualified entries have score -1."""
        votable_compo.show_voting_results = True
        votable_compo.save()
        votable_compo_entry.disqualified = True
        votable_compo_entry.save()

        base_url = f"/api/v2/public/event/{votable_compo.event_id}/kompomaatti/entries/"
        req = api_client.get(f"{base_url}{votable_compo_entry.id}/")
        assert req.status_code == 200
        assert req.data["score"] == -1.0


@pytest.mark.django_db
@freeze_time(FROZEN_TIME)
class TestCompetitionParticipationScoreRank:
    """Test competition participation score and rank via v2 public API."""

    def test_ranking_by_score_descending(self, api_client, results_competition, base_user, normal_user):
        """With default score_sort=0, highest score ranks first. Score is raw float."""
        CompetitionParticipation.objects.create(
            competition=results_competition, user=base_user, participant_name="High Score", score=200.0
        )
        CompetitionParticipation.objects.create(
            competition=results_competition, user=normal_user, participant_name="Low Score", score=50.0
        )

        base_url = (
            f"/api/v2/public/event/{results_competition.event_id}/kompomaatti/competition_participations/"
        )
        req = api_client.get(base_url)
        assert req.status_code == 200
        parts = {p["participant_name"]: p for p in req.data}

        # v2 returns raw float (not formatted string like v1)
        assert parts["High Score"]["score"] == 200.0
        assert parts["High Score"]["rank"] == 1
        assert parts["Low Score"]["score"] == 50.0
        assert parts["Low Score"]["rank"] == 2

    def test_ranking_by_score_ascending(self, api_client, event, base_user, normal_user):
        """With score_sort=1, lowest score ranks first."""
        comp = Competition.objects.create(
            event=event,
            name="Speed Run",
            description="Fastest time wins",
            participation_end=datetime(2025, 1, 14, 12, 0, 0, tzinfo=dt_tz.utc),
            start=datetime(2025, 1, 14, 13, 0, 0, tzinfo=dt_tz.utc),
            end=datetime(2025, 1, 15, 11, 0, 0, tzinfo=dt_tz.utc),
            score_type="s",
            score_sort=1,
            show_results=True,
        )
        CompetitionParticipation.objects.create(
            competition=comp, user=base_user, participant_name="Fast Runner", score=10.5
        )
        CompetitionParticipation.objects.create(
            competition=comp, user=normal_user, participant_name="Slow Runner", score=99.0
        )

        base_url = f"/api/v2/public/event/{event.id}/kompomaatti/competition_participations/"
        req = api_client.get(base_url)
        assert req.status_code == 200
        parts = {p["participant_name"]: p for p in req.data}

        assert parts["Fast Runner"]["score"] == 10.5
        assert parts["Fast Runner"]["rank"] == 1
        assert parts["Slow Runner"]["score"] == 99.0
        assert parts["Slow Runner"]["rank"] == 2

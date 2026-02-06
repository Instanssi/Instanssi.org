"""Tests for CompetitionParticipation queryset methods (with_rank)."""

import pytest

from Instanssi.kompomaatti.models import CompetitionParticipation


@pytest.mark.django_db
def test_participation_with_no_score_gets_rank(competition_participation):
    """Test that a participation with score 0 gets a rank."""
    competition_participation.score = 0
    competition_participation.save()

    result = CompetitionParticipation.objects.filter(pk=competition_participation.pk).with_rank().first()
    assert result.computed_rank == 1


@pytest.mark.django_db
def test_participations_ranked_by_score_descending(
    competition,
    competition_participation,
    normal_user_competition_participation,
    staff_competition_participation,
):
    """Test that participations are ranked by score in descending order (higher is better)."""
    competition_participation.score = 10.0
    competition_participation.save()
    normal_user_competition_participation.score = 30.0
    normal_user_competition_participation.save()
    staff_competition_participation.score = 20.0
    staff_competition_participation.save()

    results = {p.pk: p for p in CompetitionParticipation.objects.filter(competition=competition).with_rank()}

    assert results[normal_user_competition_participation.pk].computed_rank == 1
    assert results[staff_competition_participation.pk].computed_rank == 2
    assert results[competition_participation.pk].computed_rank == 3


@pytest.mark.django_db
def test_tied_scores_get_same_rank(
    competition,
    competition_participation,
    normal_user_competition_participation,
    staff_competition_participation,
):
    """Test DenseRank behavior: tied scores get same rank, next rank is sequential."""
    competition_participation.score = 100.0
    competition_participation.save()
    normal_user_competition_participation.score = 100.0
    normal_user_competition_participation.save()
    staff_competition_participation.score = 50.0
    staff_competition_participation.save()

    results = {p.pk: p for p in CompetitionParticipation.objects.filter(competition=competition).with_rank()}

    # Both tied at rank 1
    assert results[competition_participation.pk].computed_rank == 1
    assert results[normal_user_competition_participation.pk].computed_rank == 1
    # Next rank is 2 (DenseRank), not 3
    assert results[staff_competition_participation.pk].computed_rank == 2


@pytest.mark.django_db
def test_ranks_partitioned_by_competition(
    competition,
    second_competition,
    competition_participation,
    second_competition_participation,
):
    """Test that ranks are calculated per-competition (partitioned)."""
    competition_participation.score = 100.0
    competition_participation.save()
    second_competition_participation.score = 50.0
    second_competition_participation.save()

    results = {
        p.pk: p
        for p in CompetitionParticipation.objects.filter(
            competition__in=[competition, second_competition]
        ).with_rank()
    }

    # Both should be rank 1 in their respective competitions
    assert results[competition_participation.pk].computed_rank == 1
    assert results[second_competition_participation.pk].computed_rank == 1


@pytest.mark.django_db
def test_multiple_participations_sequential_ranks(
    competition,
    competition_participation,
    normal_user_competition_participation,
    staff_competition_participation,
):
    """Test that participations with unique scores get sequential ranks."""
    competition_participation.score = 30.0
    competition_participation.save()
    normal_user_competition_participation.score = 20.0
    normal_user_competition_participation.save()
    staff_competition_participation.score = 10.0
    staff_competition_participation.save()

    results = (
        CompetitionParticipation.objects.filter(competition=competition)
        .with_rank()
        .order_by("computed_rank")
    )
    ranks = [p.computed_rank for p in results]

    assert ranks == [1, 2, 3]


@pytest.mark.django_db
def test_zero_scores_tied_at_last_rank(
    competition,
    competition_participation,
    normal_user_competition_participation,
    staff_competition_participation,
):
    """Test that multiple participations with score 0 are tied at last rank."""
    competition_participation.score = 10.0
    competition_participation.save()
    normal_user_competition_participation.score = 0.0
    normal_user_competition_participation.save()
    staff_competition_participation.score = 0.0
    staff_competition_participation.save()

    results = {p.pk: p for p in CompetitionParticipation.objects.filter(competition=competition).with_rank()}

    assert results[competition_participation.pk].computed_rank == 1
    # Both zero-score participations tied at rank 2
    assert results[normal_user_competition_participation.pk].computed_rank == 2
    assert results[staff_competition_participation.pk].computed_rank == 2


# --- disqualification tests ---


@pytest.mark.django_db
def test_disqualified_participant_ranked_last(
    competition,
    competition_participation,
    normal_user_competition_participation,
    staff_competition_participation,
):
    """Disqualified participants are ranked last, regardless of score."""
    competition_participation.score = 100.0
    competition_participation.disqualified = True
    competition_participation.save()
    normal_user_competition_participation.score = 50.0
    normal_user_competition_participation.save()
    staff_competition_participation.score = 10.0
    staff_competition_participation.save()

    results = {p.pk: p for p in CompetitionParticipation.objects.filter(competition=competition).with_rank()}

    # Non-disqualified participants ranked normally
    assert results[normal_user_competition_participation.pk].computed_rank == 1
    assert results[staff_competition_participation.pk].computed_rank == 2
    # Disqualified participant ranked last despite highest score
    assert results[competition_participation.pk].computed_rank == 3


@pytest.mark.django_db
def test_disqualified_participant_ranked_last_lower_is_better(
    lower_is_better_competition,
    lower_competition_participation,
    lower_normal_competition_participation,
    lower_staff_competition_participation,
):
    """Disqualified participants ranked last even with score_sort=1 (lower is better)."""
    lower_competition_participation.score = 5.0  # Best time, but disqualified
    lower_competition_participation.disqualified = True
    lower_competition_participation.save()
    lower_normal_competition_participation.score = 20.0
    lower_normal_competition_participation.save()
    lower_staff_competition_participation.score = 30.0
    lower_staff_competition_participation.save()

    results = {
        p.pk: p
        for p in CompetitionParticipation.objects.filter(competition=lower_is_better_competition).with_rank()
    }

    assert results[lower_normal_competition_participation.pk].computed_rank == 1
    assert results[lower_staff_competition_participation.pk].computed_rank == 2
    assert results[lower_competition_participation.pk].computed_rank == 3


# --- score_sort tests (lower is better) ---


@pytest.mark.django_db
def test_score_sort_lower_is_better(
    lower_is_better_competition,
    lower_competition_participation,
    lower_normal_competition_participation,
    lower_staff_competition_participation,
):
    """Test that score_sort=1 ranks lower scores first (lower is better)."""
    lower_competition_participation.score = 30.0  # 30 seconds - worst
    lower_competition_participation.save()
    lower_normal_competition_participation.score = 10.0  # 10 seconds - best
    lower_normal_competition_participation.save()
    lower_staff_competition_participation.score = 20.0  # 20 seconds - middle
    lower_staff_competition_participation.save()

    results = {
        p.pk: p
        for p in CompetitionParticipation.objects.filter(competition=lower_is_better_competition).with_rank()
    }

    # Lower score = better rank
    assert results[lower_normal_competition_participation.pk].computed_rank == 1  # 10 sec
    assert results[lower_staff_competition_participation.pk].computed_rank == 2  # 20 sec
    assert results[lower_competition_participation.pk].computed_rank == 3  # 30 sec


@pytest.mark.django_db
def test_score_sort_mixed_competitions(
    competition,
    lower_is_better_competition,
    competition_participation,
    normal_user_competition_participation,
    lower_competition_participation,
    lower_normal_competition_participation,
):
    """Test that different competitions can have different score_sort values."""
    # competition has score_sort=0 (higher is better)
    competition_participation.score = 100.0
    competition_participation.save()
    normal_user_competition_participation.score = 50.0
    normal_user_competition_participation.save()

    # lower_is_better_competition has score_sort=1 (lower is better)
    lower_competition_participation.score = 50.0
    lower_competition_participation.save()
    lower_normal_competition_participation.score = 100.0
    lower_normal_competition_participation.save()

    results = {
        p.pk: p
        for p in CompetitionParticipation.objects.filter(
            competition__in=[competition, lower_is_better_competition]
        ).with_rank()
    }

    # Higher is better: 100 > 50
    assert results[competition_participation.pk].computed_rank == 1
    assert results[normal_user_competition_participation.pk].computed_rank == 2

    # Lower is better: 50 < 100
    assert results[lower_competition_participation.pk].computed_rank == 1
    assert results[lower_normal_competition_participation.pk].computed_rank == 2


@pytest.mark.django_db
def test_score_sort_lower_tied_scores(
    lower_is_better_competition,
    lower_competition_participation,
    lower_normal_competition_participation,
    lower_staff_competition_participation,
):
    """Test that tied scores work correctly with score_sort=1."""
    lower_competition_participation.score = 10.0
    lower_competition_participation.save()
    lower_normal_competition_participation.score = 10.0
    lower_normal_competition_participation.save()
    lower_staff_competition_participation.score = 20.0
    lower_staff_competition_participation.save()

    results = {
        p.pk: p
        for p in CompetitionParticipation.objects.filter(competition=lower_is_better_competition).with_rank()
    }

    # Both fastest tied at rank 1
    assert results[lower_competition_participation.pk].computed_rank == 1
    assert results[lower_normal_competition_participation.pk].computed_rank == 1
    # Slower gets rank 2 (DenseRank)
    assert results[lower_staff_competition_participation.pk].computed_rank == 2

"""Tests for kompomaatti queryset methods (with_score, with_rank)."""

import pytest

from Instanssi.kompomaatti.models import Entry, Vote, VoteGroup

# --- Score calculation tests ---


@pytest.mark.django_db
def test_entry_with_no_votes_gets_zero_score(votable_compo_entry):
    """Test that an entry with no votes gets score 0.0."""
    result = Entry.objects.filter(pk=votable_compo_entry.pk).with_score().first()
    assert result.computed_score == 0.0


@pytest.mark.django_db
def test_score_calculation_single_voter(
    votable_compo, votable_compo_entry, second_votable_entry, third_votable_entry, base_user
):
    """Test score calculation with a single voter.

    Score = sum(1/rank) for each vote on the entry.
    """
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=1
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=second_votable_entry, rank=2
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=third_votable_entry, rank=3
    )

    scores = {e.pk: e.computed_score for e in Entry.objects.filter(compo=votable_compo).with_score()}

    assert scores[votable_compo_entry.pk] == 1.0  # 1/1
    assert scores[second_votable_entry.pk] == 0.5  # 1/2
    assert abs(scores[third_votable_entry.pk] - 1 / 3) < 0.0001  # 1/3


@pytest.mark.django_db
def test_score_calculation_multiple_voters(votable_compo, votable_compo_entry, base_user, normal_user):
    """Test score aggregation across multiple voters."""
    # First voter gives rank 1 (score contribution: 1.0)
    vote_group1 = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group1, compo=votable_compo, entry=votable_compo_entry, rank=1
    )

    # Second voter gives rank 2 (score contribution: 0.5)
    vote_group2 = VoteGroup.objects.create(user=normal_user, compo=votable_compo)
    Vote.objects.create(
        user=normal_user, group=vote_group2, compo=votable_compo, entry=votable_compo_entry, rank=2
    )

    result = Entry.objects.filter(pk=votable_compo_entry.pk).with_score().first()
    assert result.computed_score == 1.5  # 1/1 + 1/2


@pytest.mark.django_db
def test_disqualified_entry_gets_negative_score(votable_compo, base_user):
    """Test that disqualified entries get score -1.0 regardless of votes."""
    entry = Entry.objects.create(
        user=base_user,
        compo=votable_compo,
        name="Disqualified Entry",
        description="This entry is disqualified",
        creator="Creator",
        entryfile="test.zip",
        disqualified=True,
    )

    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(user=base_user, group=vote_group, compo=votable_compo, entry=entry, rank=1)

    result = Entry.objects.filter(pk=entry.pk).with_score().first()
    assert result.computed_score == -1.0


@pytest.mark.django_db
def test_archived_entry_uses_archive_score(votable_compo, base_user):
    """Test that entries with archive_score use that instead of calculated score."""
    entry = Entry.objects.create(
        user=base_user,
        compo=votable_compo,
        name="Archived Entry",
        description="Entry with archive score",
        creator="Creator",
        entryfile="test.zip",
        archive_score=42.5,
    )

    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(user=base_user, group=vote_group, compo=votable_compo, entry=entry, rank=1)

    result = Entry.objects.filter(pk=entry.pk).with_score().first()
    assert result.computed_score == 42.5  # Uses archive_score, not calculated


# --- Rank calculation tests ---


@pytest.mark.django_db
def test_entries_ranked_by_score_descending(
    votable_compo, votable_compo_entry, second_votable_entry, third_votable_entry, base_user
):
    """Test that entries are ranked by score in descending order."""
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    # Give second_votable_entry the best rank, then votable_compo_entry, then third
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=second_votable_entry, rank=1
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=2
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=third_votable_entry, rank=3
    )

    results = {e.pk: e for e in Entry.objects.filter(compo=votable_compo).with_rank()}

    assert results[second_votable_entry.pk].computed_rank == 1  # Highest score
    assert results[votable_compo_entry.pk].computed_rank == 2
    assert results[third_votable_entry.pk].computed_rank == 3  # Lowest score


@pytest.mark.django_db
def test_tied_scores_get_same_rank_with_sequential_next(
    votable_compo, votable_compo_entry, second_votable_entry, third_votable_entry, base_user
):
    """Test DenseRank behavior: tied scores get same rank, next rank is sequential."""
    # Both votable_compo_entry and second_votable_entry get rank 1 votes (score = 1.0 each)
    # third_votable_entry gets rank 2 vote (score = 0.5)
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=1
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=second_votable_entry, rank=1
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=third_votable_entry, rank=2
    )

    results = {e.pk: e for e in Entry.objects.filter(compo=votable_compo).with_rank()}

    # Tied at rank 1
    assert results[votable_compo_entry.pk].computed_rank == 1
    assert results[second_votable_entry.pk].computed_rank == 1
    # DenseRank: sequential, not skipping to 3
    assert results[third_votable_entry.pk].computed_rank == 2


@pytest.mark.django_db
def test_unique_scores_get_sequential_ranks(
    votable_compo, votable_compo_entry, second_votable_entry, third_votable_entry, base_user
):
    """Test that entries with unique scores get sequential ranks 1, 2, 3."""
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=1
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=second_votable_entry, rank=2
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=third_votable_entry, rank=3
    )

    entries = Entry.objects.filter(compo=votable_compo).with_rank().order_by("computed_rank")
    ranks = [e.computed_rank for e in entries]
    assert ranks == [1, 2, 3]


@pytest.mark.django_db
def test_archived_entry_uses_archive_rank(votable_compo, base_user):
    """Test that entries with archive_rank use that instead of calculated rank."""
    entry = Entry.objects.create(
        user=base_user,
        compo=votable_compo,
        name="Archived Entry",
        description="Entry with archive rank",
        creator="Creator",
        entryfile="test.zip",
        archive_rank=5,
        archive_score=42.0,
    )

    result = Entry.objects.filter(pk=entry.pk).with_rank().first()
    assert result.computed_rank == 5
    assert result.computed_score == 42.0


@pytest.mark.django_db
def test_ranks_partitioned_by_compo(votable_compo, second_votable_compo, votable_compo_entry, base_user):
    """Test that ranks are calculated per-compo (partitioned)."""
    entry_in_compo2 = Entry.objects.create(
        user=base_user,
        compo=second_votable_compo,
        name="Entry in Compo 2",
        description="Entry",
        creator="Creator",
        entryfile="test2.zip",
    )

    vote_group1 = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group1, compo=votable_compo, entry=votable_compo_entry, rank=1
    )

    vote_group2 = VoteGroup.objects.create(user=base_user, compo=second_votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group2, compo=second_votable_compo, entry=entry_in_compo2, rank=1
    )

    results = {
        e.pk: e for e in Entry.objects.filter(compo__in=[votable_compo, second_votable_compo]).with_rank()
    }

    # Both should be rank 1 in their respective compos
    assert results[votable_compo_entry.pk].computed_rank == 1
    assert results[entry_in_compo2.pk].computed_rank == 1


@pytest.mark.django_db
def test_entry_with_no_votes_ranked_last(
    votable_compo, votable_compo_entry, second_votable_entry, base_user
):
    """Test that an entry with no votes gets ranked after voted entries."""
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=1
    )

    results = {e.pk: e for e in Entry.objects.filter(compo=votable_compo).with_rank()}

    assert results[votable_compo_entry.pk].computed_rank == 1
    assert results[votable_compo_entry.pk].computed_score == 1.0
    assert results[second_votable_entry.pk].computed_rank == 2
    assert results[second_votable_entry.pk].computed_score == 0.0


@pytest.mark.django_db
def test_disqualified_entry_ranked_last(votable_compo, votable_compo_entry, base_user):
    """Test that disqualified entries (score -1) are ranked last."""
    disqualified_entry = Entry.objects.create(
        user=base_user,
        compo=votable_compo,
        name="Disqualified Entry",
        description="Entry",
        creator="Creator",
        entryfile="test2.zip",
        disqualified=True,
    )

    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=2
    )
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=disqualified_entry, rank=1
    )

    results = {e.pk: e for e in Entry.objects.filter(compo=votable_compo).with_rank()}

    # Normal entry should be rank 1, disqualified is rank 2 (despite having "better" vote)
    assert results[votable_compo_entry.pk].computed_rank == 1
    assert results[votable_compo_entry.pk].computed_score == 0.5
    assert results[disqualified_entry.pk].computed_rank == 2
    assert results[disqualified_entry.pk].computed_score == -1.0


@pytest.mark.django_db
def test_multiple_unvoted_entries_tied_at_last_rank(
    votable_compo, votable_compo_entry, second_votable_entry, third_votable_entry, base_user
):
    """Test that multiple entries with no votes are tied at the last rank."""
    vote_group = VoteGroup.objects.create(user=base_user, compo=votable_compo)
    Vote.objects.create(
        user=base_user, group=vote_group, compo=votable_compo, entry=votable_compo_entry, rank=1
    )

    results = {e.pk: e for e in Entry.objects.filter(compo=votable_compo).with_rank()}

    assert results[votable_compo_entry.pk].computed_rank == 1
    # Both unvoted entries should be tied at rank 2 (both have computed_score 0.0)
    assert results[second_votable_entry.pk].computed_rank == 2
    assert results[third_votable_entry.pk].computed_rank == 2

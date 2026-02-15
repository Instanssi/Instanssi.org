from __future__ import annotations

from typing import TYPE_CHECKING

from django.db.models import (
    Case,
    F,
    FloatField,
    IntegerField,
    OuterRef,
    QuerySet,
    Subquery,
    Sum,
    Value,
    When,
    Window,
)
from django.db.models.functions import Coalesce, DenseRank

if TYPE_CHECKING:
    from Instanssi.kompomaatti.models import CompetitionParticipation, Entry


class EntryQuerySet(QuerySet["Entry"]):
    """Custom QuerySet for Entry with score and rank annotations."""

    def with_score(self) -> EntryQuerySet:
        """Annotate entries with score.

        Score is calculated as:
        - -1.0 if entry is disqualified
        - archive_score if set (for archived events)
        - Otherwise: SUM(1.0 / vote.rank) across all votes
        """
        from Instanssi.kompomaatti.models import Vote

        vote_score = (
            Vote.objects.filter(entry_id=OuterRef("pk"))
            .values("entry_id")
            .annotate(total=Sum(Value(1.0, output_field=FloatField()) / F("rank")))
            .values("total")
        )

        return self.annotate(
            computed_score=Case(  # type: ignore[no-redef]
                When(disqualified=True, then=Value(-1.0, output_field=FloatField())),
                When(archive_score__isnull=False, then=F("archive_score")),
                default=Coalesce(Subquery(vote_score), Value(0.0, output_field=FloatField())),
                output_field=FloatField(),
            )
        )

    def with_rank(self) -> EntryQuerySet:
        """Annotate entries with score and rank.

        Rank is calculated as:
        - archive_rank if set (for archived events)
        - Otherwise: DENSE_RANK() window function over score, partitioned by compo
          (uses dense rank so ties get same rank but next rank is sequential, not skipped)
        """
        return self.with_score().annotate(
            computed_rank=Case(  # type: ignore[no-redef]
                When(archive_rank__isnull=False, then=F("archive_rank")),
                default=Window(
                    expression=DenseRank(),
                    partition_by=[F("compo_id")],
                    order_by=F("computed_score").desc(),
                ),
                output_field=IntegerField(),
            )
        )


class CompetitionParticipationQuerySet(QuerySet["CompetitionParticipation"]):
    """Custom QuerySet for CompetitionParticipation with rank annotation."""

    def with_rank(self) -> CompetitionParticipationQuerySet:
        """Annotate participations with rank.

        Rank is calculated using DENSE_RANK() window function over score,
        partitioned by competition. The sort order depends on competition.score_sort:
        - score_sort=0: Higher score is better (default, descending order)
        - score_sort=1: Lower score is better (ascending order)

        To handle both cases with a single window function, we compute a
        "normalized score" that negates the score when score_sort=1, allowing
        us to always sort descending.
        """
        # Normalize score: negate when score_sort=1 so descending order gives correct rank.
        # Disqualified participants get a sentinel value that sorts last (below all real scores).
        normalized_score = Case(
            When(disqualified=True, then=Value(float("-inf"), output_field=FloatField())),
            When(competition__score_sort=1, then=-F("score")),
            default=F("score"),
            output_field=FloatField(),
        )
        return self.annotate(
            computed_rank=Window(  # type: ignore[no-redef]
                expression=DenseRank(),
                partition_by=[F("competition_id")],
                order_by=normalized_score.desc(),
            )
        )

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import CompetitionParticipation


class PublicCompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    """Public serializer for competition participations.

    Drops sensitive/staff-only fields: user FK, disqualified_reason.
    Rank/score/disqualified are shown only when competition.show_results is True.
    """

    rank = SerializerMethodField()
    score = SerializerMethodField()
    disqualified = SerializerMethodField()
    disqualified_reason = SerializerMethodField()

    def get_rank(self, obj: CompetitionParticipation) -> int | None:
        if obj.competition.show_results:
            return obj.computed_rank
        return None

    def get_score(self, obj: CompetitionParticipation) -> float | None:
        if obj.competition.show_results:
            return obj.score
        return None

    def get_disqualified(self, obj: CompetitionParticipation) -> bool | None:
        if obj.competition.show_results:
            return obj.disqualified
        return None

    def get_disqualified_reason(self, obj: CompetitionParticipation) -> str | None:
        if obj.competition.show_results:
            return obj.disqualified_reason
        return None

    class Meta:
        model = CompetitionParticipation
        fields = (
            "id",
            "competition",
            "participant_name",
            "score",
            "disqualified",
            "disqualified_reason",
            "rank",
        )

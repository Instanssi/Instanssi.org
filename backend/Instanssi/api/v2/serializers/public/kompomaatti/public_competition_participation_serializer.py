from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import CompetitionParticipation


class PublicCompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    """Public serializer for competition participations.

    Drops sensitive/staff-only fields: user FK, disqualified_reason.
    Rank/score are shown only when competition.show_results is True.
    """

    rank = SerializerMethodField()
    score = SerializerMethodField()

    def get_rank(self, obj: CompetitionParticipation) -> int | None:
        if obj.competition.show_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: CompetitionParticipation) -> float | None:
        if obj.competition.show_results:
            return obj.score
        return None

    class Meta:
        model = CompetitionParticipation
        fields = (
            "id",
            "competition",
            "participant_name",
            "score",
            "disqualified",
            "rank",
        )

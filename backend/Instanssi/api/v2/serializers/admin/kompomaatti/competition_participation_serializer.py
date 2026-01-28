from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import CompetitionParticipation


class CompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    """Staff serializer for competition participations."""

    rank = SerializerMethodField()

    def get_rank(self, obj: CompetitionParticipation) -> int | None:
        return obj.get_rank()

    class Meta:
        model = CompetitionParticipation
        fields = (
            "id",
            "competition",
            "user",
            "participant_name",
            "score",
            "disqualified",
            "disqualified_reason",
            "rank",
        )
        read_only_fields = ("rank",)
        extra_kwargs = {
            "score": {"required": False},
        }

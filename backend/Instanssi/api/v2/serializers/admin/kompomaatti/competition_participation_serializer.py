from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import CompetitionParticipation


class CompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    """Staff serializer for competition participations.

    Requires queryset to have with_rank() annotation applied.
    """

    computed_rank = SerializerMethodField()

    def get_computed_rank(self, obj: CompetitionParticipation) -> int:
        return obj.computed_rank

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
            "computed_rank",
        )
        read_only_fields = ("computed_rank",)
        extra_kwargs = {
            "score": {"required": False},
        }

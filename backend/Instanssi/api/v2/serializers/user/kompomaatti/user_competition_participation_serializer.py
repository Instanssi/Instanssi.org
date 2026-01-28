from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField

from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class UserCompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    """User serializer for managing own competition participations."""

    competition = PrimaryKeyRelatedField(queryset=Competition.objects.all())

    class Meta:
        model = CompetitionParticipation
        fields = ("id", "competition", "participant_name")
        extra_kwargs = {
            "id": {"read_only": True},
        }

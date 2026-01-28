from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Competition


class PublicCompetitionSerializer(ModelSerializer[Competition]):
    """Public read-only serializer for competitions."""

    class Meta:
        model = Competition
        fields = (
            "id",
            "event",
            "name",
            "description",
            "participation_end",
            "start",
            "end",
            "score_type",
            "score_sort",
            "show_results",
        )

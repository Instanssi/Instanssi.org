from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import Competition


class CompetitionSerializer(ModelSerializer[Competition]):
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
            "active",
            "hide_from_archive",
        )
        read_only_fields = ("event",)  # Set from URL, not request body

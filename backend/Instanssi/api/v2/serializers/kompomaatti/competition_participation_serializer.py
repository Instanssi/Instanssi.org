from typing import Any

from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.kompomaatti.models import CompetitionParticipation


class CompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    rank = SerializerMethodField()

    def get_rank(self, obj: CompetitionParticipation) -> int | None:
        # Show rank only if user has permissions or show_results is enabled
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm("kompomaatti.view_competitionparticipation")
        ):
            return obj.get_rank()
        if obj.competition.show_results:
            return obj.get_rank()
        return None

    def get_score(self, obj: CompetitionParticipation) -> float | None:
        # Show score only if user has permissions or show_results is enabled
        request = self.context.get("request")
        if (
            request
            and request.user.is_authenticated
            and request.user.has_perm("kompomaatti.view_competitionparticipation")
        ):
            return obj.score
        if obj.competition.show_results:
            return obj.score
        return None

    def to_representation(self, instance: CompetitionParticipation) -> dict[str, Any]:
        """Apply conditional visibility to score field"""
        data: dict[str, Any] = super().to_representation(instance)
        data["score"] = self.get_score(instance)
        return data

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

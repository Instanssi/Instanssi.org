from typing import Any

from rest_framework.serializers import (
    ModelSerializer,
    PrimaryKeyRelatedField,
    ValidationError,
)

from Instanssi.kompomaatti.models import Competition, CompetitionParticipation


class UserCompetitionParticipationSerializer(ModelSerializer[CompetitionParticipation]):
    competition = PrimaryKeyRelatedField(queryset=Competition.objects.filter(active=True))

    def validate_competition(self, competition: Competition) -> Competition:
        if not competition.active:
            raise ValidationError("Competition is not active")
        return competition

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        data = super().validate(data)

        competition = data.get("competition")
        if not competition:
            if self.instance:
                competition = self.instance.competition
            else:
                raise ValidationError({"competition": ["This field is required."]})

        # Check if participation is still open
        if not competition.is_participating_open():
            raise ValidationError({"competition": ["Competition participation time has ended"]})

        # Check for duplicate participation (only for new instances or when changing competition)
        request = self.context.get("request")
        if request and request.user:
            has_changed = self.instance and self.instance.competition_id != competition.id
            if not self.instance or has_changed:
                existing = CompetitionParticipation.objects.filter(
                    competition=competition, user=request.user
                ).first()
                if existing:
                    raise ValidationError(
                        {"competition": ["You have already participated in this competition"]}
                    )

        return data

    class Meta:
        model = CompetitionParticipation
        fields = ("id", "competition", "participant_name")
        extra_kwargs = {
            "id": {"read_only": True},
        }

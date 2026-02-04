import logging

from rest_framework.serializers import ModelSerializer

from Instanssi.ext_programme.models import ProgrammeEvent

logger = logging.getLogger(__name__)


class ProgrammeEventSerializer(ModelSerializer[ProgrammeEvent]):
    class Meta:
        model = ProgrammeEvent
        fields = (
            "id",
            "event",
            "start",
            "end",
            "description",
            "title",
            "presenters",
            "presenters_titles",
            "place",
        )

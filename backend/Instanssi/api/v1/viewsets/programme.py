import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v1.serializers.programme import ProgrammeEventSerializer
from Instanssi.ext_programme.models import ProgrammeEvent

logger = logging.getLogger(__name__)


class ProgrammeEventViewSet(ReadOnlyModelViewSet):
    """
    Exposes all programme events.

    Allows GET filters:
    * limit: Limit amount of returned objects.
    * offset: Starting offset. Default is 0.
    * event: Filter by event id
    * ordering: Set ordering, default is 'id'. Allowed: id, -id
    """

    queryset = ProgrammeEvent.objects.filter(active=True, event__hidden=False)
    serializer_class = ProgrammeEventSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id",)
    filterset_fields = ("event",)

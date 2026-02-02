from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from Instanssi.api.v2.serializers.public import PublicEventSerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.kompomaatti.models import Event


class PublicEventViewSet(PublicReadOnlyViewSet[Event]):
    """Public read-only endpoint for events."""

    serializer_class = PublicEventSerializer
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "name", "date", "tag")
    search_fields = ("name", "tag")
    filterset_fields = ("archived",)
    queryset = Event.objects.all()

    def get_queryset(self) -> QuerySet[Event]:
        return Event.objects.filter(hidden=False)

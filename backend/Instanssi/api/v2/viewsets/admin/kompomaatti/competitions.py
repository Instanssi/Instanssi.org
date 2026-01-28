from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.serializers import BaseSerializer

from Instanssi.api.v2.serializers.admin.kompomaatti import CompetitionSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Competition


class CompetitionViewSet(PermissionViewSet):
    queryset = Competition.objects.all()
    serializer_class = CompetitionSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "event", "name", "start")
    search_fields = ("name", "description")
    filterset_fields = ("active", "show_results", "hide_from_archive")

    def get_queryset(self) -> QuerySet[Competition]:
        """Filter competitions by event from URL."""
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(event_id=event_id)

    def perform_create(self, serializer: BaseSerializer[Competition]) -> None:  # type: ignore[override]
        """Set event from URL when creating."""
        serializer.save(event_id=int(self.kwargs["event_pk"]))

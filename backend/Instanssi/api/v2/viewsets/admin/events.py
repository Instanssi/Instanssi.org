from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.admin.events import EventSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.kompomaatti.models import Event


class EventViewSet(PermissionViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "name", "date", "tag")
    search_fields = ("name", "tag")

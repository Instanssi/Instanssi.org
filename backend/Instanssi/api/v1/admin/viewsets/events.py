from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v1.admin.serializers.events import AdminEventSerializer
from Instanssi.api.v1.admin.viewsets.base import AdminReadOnlyViewSet
from Instanssi.kompomaatti.models import Event


class AdminEventViewSet(AdminReadOnlyViewSet[Event]):
    queryset = Event.objects.all()
    serializer_class = AdminEventSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "name", "date")
    filterset_fields = ("name", "date")

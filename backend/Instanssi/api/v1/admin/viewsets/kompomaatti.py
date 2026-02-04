from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v1.admin.serializers.kompomaatti import (
    AdminCompoEntrySerializer,
    AdminCompoSerializer,
)
from Instanssi.api.v1.admin.viewsets.base import AdminReadOnlyViewSet
from Instanssi.kompomaatti.models import Compo, Entry


class AdminCompoViewSet(AdminReadOnlyViewSet[Compo]):
    queryset = Compo.objects.all()
    serializer_class = AdminCompoSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "event")
    filterset_fields = (
        "event",
        "active",
        "show_voting_results",
        "is_votable",
        "hide_from_archive",
        "hide_from_frontpage",
    )


class AdminCompoEntryViewSet(AdminReadOnlyViewSet[Entry]):
    queryset = Entry.objects.all()
    serializer_class = AdminCompoEntrySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "compo")
    filterset_fields = ("compo", "disqualified", "user")

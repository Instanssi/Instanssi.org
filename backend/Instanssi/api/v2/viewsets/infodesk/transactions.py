from typing import Sequence

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v2.serializers.infodesk import InfodeskTransactionSerializer
from Instanssi.api.v2.viewsets.infodesk.permissions import HasInfodeskViewPermission
from Instanssi.store.models import StoreTransaction


class InfodeskTransactionViewSet(ReadOnlyModelViewSet[StoreTransaction]):
    """Infodesk viewset for looking up transactions."""

    queryset = StoreTransaction.objects.all()
    serializer_class = InfodeskTransactionSerializer
    permission_classes = [IsAdminUser, HasInfodeskViewPermission]
    pagination_class = LimitOffsetPagination
    filter_backends: Sequence[type] = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering = ("-time_created",)
    ordering_fields = ("id", "time_created", "firstname", "lastname")
    search_fields = ("firstname", "lastname", "email")

    def get_queryset(self) -> QuerySet[StoreTransaction]:
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(transactionitem__item__event_id=event_id)
            .distinct()
            .order_by("-time_created")
        )

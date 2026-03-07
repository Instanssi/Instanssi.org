import logging
from typing import Sequence

from django.db.models import QuerySet
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v2.serializers.infodesk import InfodeskTransactionItemSerializer
from Instanssi.api.v2.viewsets.infodesk.permissions import (
    HasInfodeskChangePermission,
    HasInfodeskViewPermission,
)
from Instanssi.store.models import TransactionItem

logger = logging.getLogger(__name__)


class InfodeskTransactionItemViewSet(ReadOnlyModelViewSet[TransactionItem]):
    """Infodesk viewset for looking up and marking transaction items."""

    queryset = TransactionItem.objects.select_related("item", "variant", "transaction").all()
    serializer_class = InfodeskTransactionItemSerializer
    permission_classes = [IsAdminUser, HasInfodeskViewPermission]
    pagination_class = LimitOffsetPagination
    filter_backends: Sequence[type] = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering = ("-id",)
    ordering_fields = ("id", "time_delivered")
    search_fields = ("key", "transaction__firstname", "transaction__lastname", "transaction__email")
    filterset_fields = ("transaction",)

    def get_queryset(self) -> QuerySet[TransactionItem]:
        event_id = int(self.kwargs["event_pk"])
        return self.queryset.filter(item__event_id=event_id)

    @action(detail=True, methods=["post"], permission_classes=[IsAdminUser, HasInfodeskChangePermission])
    def mark_delivered(self, request: Request, pk: int | None = None, **kwargs: int) -> Response:
        """Mark a transaction item as delivered."""
        item = self.get_object()
        if item.is_delivered:
            serializer = self.get_serializer(item)
            return Response(serializer.data)
        item.time_delivered = timezone.now()
        item.save(update_fields=["time_delivered"])
        if item.transaction.is_paid:
            logger.info("Item %d marked as delivered.", item.id, extra={"user": request.user})
        else:
            logger.info(
                "Item %d marked as delivered (no payment recorded!)",
                item.id,
                extra={"user": request.user},
            )
        serializer = self.get_serializer(item)
        return Response(serializer.data)

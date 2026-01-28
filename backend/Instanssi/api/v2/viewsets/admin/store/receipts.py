from typing import Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.serializers.admin.store.receipt_serializer import (
    ReceiptSerializer,
)
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import Receipt


class ReceiptViewSet(PermissionViewSet):
    """ViewSet for Receipt model (staff access).

    Staff access (requires store.view/add/change/delete_receipt permissions):
    - GET: List/retrieve all receipts
    - POST: Create new receipts
    - PUT/PATCH: Update receipts (e.g., change mail_to)
    - DELETE: Delete receipts

    Custom actions:
    - POST /receipts/<id>/resend/: Resend the receipt email
    """

    queryset = Receipt.objects.all()
    serializer_class = ReceiptSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "sent", "mail_to", "subject")
    search_fields = ("mail_to", "subject")
    filterset_fields = ("transaction", "sent")

    def get_queryset(self) -> QuerySet[Receipt]:
        return self.queryset.select_related("transaction").order_by("-id")

    @action(detail=True, methods=["post"])
    def resend(self, request: Request, pk: str | None = None, **kwargs: Any) -> Response:
        """Resend the receipt email."""
        receipt: Receipt = self.get_object()  # type: ignore[assignment]

        if not receipt.content:
            return Response(
                {"detail": "Receipt has no content to send."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        receipt.send()
        serializer = self.get_serializer(receipt)
        return Response(serializer.data)

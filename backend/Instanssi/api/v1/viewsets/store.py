import logging
from typing import Any

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from Instanssi.api.v1.serializers.store import (
    StoreItemSerializer,
    StoreTransactionSerializer,
)
from Instanssi.api.v1.utils import IsAuthenticatedOrWriteOnly, WriteOnlyModelViewSet
from Instanssi.store.handlers import begin_payment_process
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreItem, StoreTransaction

logger = logging.getLogger(__name__)


class StoreItemViewSet(ReadOnlyModelViewSet[StoreItem]):
    """
    Exposes all available store items.  This entrypoint does not require authentication/authorization.
    """

    serializer_class = StoreItemSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes: list[Any] = []

    def get_queryset(self) -> QuerySet[StoreItem]:
        return StoreItem.items_visible(secret_key=self.request.query_params.get("secret_key"))


class StoreTransactionViewSet(WriteOnlyModelViewSet[StoreTransaction]):
    """
    Handles saving store transactions. This entrypoint does not require authentication/authorization.
    """

    serializer_class = StoreTransactionSerializer
    permission_classes = [IsAuthenticatedOrWriteOnly]
    authentication_classes: list[Any] = []

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["save"]:
                ta = serializer.save()
                payment_method = PaymentMethod(serializer.validated_data["payment_method"])
                response_url = begin_payment_process(request, payment_method, ta)
                return Response({"url": response_url}, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

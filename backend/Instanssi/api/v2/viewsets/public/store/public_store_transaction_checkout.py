from typing import Any

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.serializers.public.store import (
    PublicStoreTransactionCheckoutSerializer,
)
from Instanssi.api.v2.utils.base import WriteOnlyModelViewSet
from Instanssi.store.handlers import begin_payment_process
from Instanssi.store.methods import PaymentMethod
from Instanssi.store.models import StoreTransaction


class PublicStoreTransactionCheckoutViewSet(WriteOnlyModelViewSet):
    """Public ViewSet for creating store transactions (checkout).

    This endpoint allows anonymous users to create store transactions.
    No authentication is required.

    POST: Create a new transaction and return the payment URL.
    """

    serializer_class = PublicStoreTransactionCheckoutSerializer  # type: ignore[assignment]
    permission_classes = [AllowAny]
    authentication_classes: list[type] = []

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if serializer.validated_data["confirm"]:
                ta: StoreTransaction = serializer.save()  # type: ignore[assignment]
                payment_method = PaymentMethod(serializer.validated_data["payment_method"])
                response_url = begin_payment_process(request, payment_method, ta)
                return Response({"url": response_url}, status=status.HTTP_201_CREATED)
            else:
                return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

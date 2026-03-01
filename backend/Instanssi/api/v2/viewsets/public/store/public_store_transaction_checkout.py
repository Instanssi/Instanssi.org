from typing import Any

from django.utils.translation import gettext as _
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from Instanssi.api.v2.serializers.public.store import (
    PublicStoreTransactionCheckoutSerializer,
)
from Instanssi.api.v2.utils.base import WriteOnlyModelViewSet
from Instanssi.store.handlers import (
    TransactionException,
    begin_payment_process,
    create_store_transaction,
    validate_item,
    validate_items,
    validate_payment_method,
)
from Instanssi.store.methods import PaymentMethod


class PublicStoreTransactionCheckoutViewSet(WriteOnlyModelViewSet):
    """Public ViewSet for creating store transactions (checkout).

    This endpoint allows anonymous users to create store transactions.
    No authentication is required.

    POST: Create a new transaction and return the payment URL.
    """

    serializer_class = PublicStoreTransactionCheckoutSerializer  # type: ignore[assignment]
    permission_classes = [AllowAny]
    authentication_classes: list[type] = []

    def _validate_checkout(self, data: dict[str, Any]) -> None:
        """Validate checkout business rules after deserialization."""
        if not data["read_terms"]:
            raise ValidationError(
                {"read_terms": [_("Terms and conditions must be accepted before proceeding with the order")]}
            )

        items = data.get("items")
        if not items:
            raise ValidationError({"items": [_("Shopping cart must contain at least one item")]})

        try:
            for item in items:
                validate_item(item)
            validate_items(items)
            validate_payment_method(items, PaymentMethod(data["payment_method"]))
        except TransactionException as e:
            raise ValidationError(str(e))

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self._validate_checkout(serializer.validated_data)
        if serializer.validated_data["confirm"]:
            ta = create_store_transaction(serializer.validated_data)
            payment_method = PaymentMethod(serializer.validated_data["payment_method"])
            response_url = begin_payment_process(request, payment_method, ta)
            return Response({"url": response_url}, status=status.HTTP_201_CREATED)
        else:
            return Response(status=status.HTTP_200_OK)

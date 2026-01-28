from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.admin.store import StoreTransactionSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreTransaction


class StoreTransactionViewSet(PermissionViewSet):
    """ViewSet for StoreTransaction model (staff access).

    Staff access (requires store.view/add/change/delete_storetransaction permissions):
    - GET: List/retrieve all store transactions
    - POST: Create new store transactions
    - PUT/PATCH: Update store transactions
    - DELETE: Delete store transactions
    """

    queryset = StoreTransaction.objects.all()
    serializer_class = StoreTransactionSerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "time_created", "time_paid", "firstname", "lastname")
    search_fields = ("firstname", "lastname", "email", "key")
    filterset_fields = ("time_paid", "time_cancelled")

    def get_queryset(self) -> QuerySet[StoreTransaction]:
        """Filter transactions by event if specified."""
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(transactionitem__item__event_id=event_id)
            .prefetch_related("transactionitem_set", "storetransactionevent_set", "receipt_set")
            .distinct()
            .order_by("-time_created")
        )

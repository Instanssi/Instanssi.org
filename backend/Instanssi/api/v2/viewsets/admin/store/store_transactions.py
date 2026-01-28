from django.db.models import QuerySet

from Instanssi.api.v2.serializers.admin.store import StoreTransactionSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.store.models import StoreTransaction


class StoreTransactionViewSet(PermissionViewSet):
    """Staff viewset for managing store transactions."""

    queryset = StoreTransaction.objects.all()
    serializer_class = StoreTransactionSerializer  # type: ignore[assignment]
    ordering_fields = ("id", "time_created", "time_paid", "firstname", "lastname")
    search_fields = ("firstname", "lastname", "email", "key")
    filterset_fields = ("time_paid", "time_cancelled")

    def get_queryset(self) -> QuerySet[StoreTransaction]:
        """Filter transactions by event."""
        event_id = int(self.kwargs["event_pk"])
        return (
            self.queryset.filter(transactionitem__item__event_id=event_id)
            .prefetch_related("transactionitem_set", "storetransactionevent_set", "receipt_set")
            .distinct()
            .order_by("-time_created")
        )

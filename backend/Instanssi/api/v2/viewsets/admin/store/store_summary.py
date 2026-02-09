from decimal import Decimal
from typing import Any
from zoneinfo import ZoneInfo

from django.db.models import Count, Sum
from django.db.models.functions import ExtractHour, TruncDate
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from Instanssi.api.v2.serializers.admin.store import StoreSummarySerializer
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions
from Instanssi.store.models import StoreItem, TransactionItem

HELSINKI_TZ = ZoneInfo("Europe/Helsinki")


class StoreSummaryViewSet(GenericViewSet[StoreItem]):
    """Staff viewset for aggregated store sales summary.

    Returns pre-aggregated statistics (totals, per-item breakdown,
    sales per day, sales per hour) without exposing any PII.
    Permission is derived from StoreItem (store.view_storeitem).
    """

    permission_classes = [FullDjangoModelPermissions]
    queryset = StoreItem.objects.all()
    serializer_class = StoreSummarySerializer
    pagination_class = None

    def list(self, request: Request, **kwargs: Any) -> Response:
        event_pk = int(self.kwargs["event_pk"])

        # Base queryset: only items from paid transactions for this event
        base_qs = TransactionItem.objects.filter(
            item__event_id=event_pk,
            transaction__time_paid__isnull=False,
        )

        # Totals
        totals = base_qs.aggregate(
            total_items_sold=Count("id"),
            total_revenue=Sum("purchase_price"),
        )

        # Per-item/variant breakdown
        items_qs = (
            base_qs.values("item__id", "item__name", "variant__id", "variant__name")
            .annotate(quantity=Count("id"), revenue=Sum("purchase_price"))
            .order_by("item__name", "variant__name")
        )
        items = [
            {
                "item_id": row["item__id"],
                "item_name": row["item__name"],
                "variant_id": row["variant__id"],
                "variant_name": row["variant__name"],
                "quantity": row["quantity"],
                "revenue": row["revenue"],
            }
            for row in items_qs
        ]

        # Sales per day (in Helsinki timezone)
        day_qs = (
            base_qs.annotate(date=TruncDate("transaction__time_paid", tzinfo=HELSINKI_TZ))
            .values("date")
            .annotate(count=Count("id"))
            .order_by("date")
        )
        sales_per_day = [{"date": row["date"], "count": row["count"]} for row in day_qs]

        # Sales per hour (in Helsinki timezone)
        hour_qs = (
            base_qs.annotate(hour=ExtractHour("transaction__time_paid", tzinfo=HELSINKI_TZ))
            .values("hour")
            .annotate(count=Count("id"))
            .order_by("hour")
        )
        sales_per_hour = [{"hour": row["hour"], "count": row["count"]} for row in hour_qs]

        data = {
            "total_items_sold": totals["total_items_sold"] or 0,
            "total_revenue": totals["total_revenue"] or Decimal(0),
            "items": items,
            "sales_per_day": sales_per_day,
            "sales_per_hour": sales_per_hour,
        }

        serializer = StoreSummarySerializer(data)
        return Response(serializer.data)

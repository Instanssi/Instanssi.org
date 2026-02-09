from typing import Any

from drf_spectacular.utils import extend_schema_serializer
from rest_framework import serializers


class StoreSummaryItemRow(serializers.Serializer[Any]):
    item_id = serializers.IntegerField()
    item_name = serializers.CharField()
    variant_id = serializers.IntegerField(allow_null=True)
    variant_name = serializers.CharField(allow_null=True)
    quantity = serializers.IntegerField()
    revenue = serializers.CharField()


class StoreSummaryDayRow(serializers.Serializer[Any]):
    date = serializers.DateField()
    count = serializers.IntegerField()


class StoreSummaryHourRow(serializers.Serializer[Any]):
    hour = serializers.IntegerField()
    count = serializers.IntegerField()


@extend_schema_serializer(many=False)
class StoreSummarySerializer(serializers.Serializer[Any]):
    total_items_sold = serializers.IntegerField()
    total_revenue = serializers.CharField()
    items = StoreSummaryItemRow(many=True)
    sales_per_day = StoreSummaryDayRow(many=True)
    sales_per_hour = StoreSummaryHourRow(many=True)

from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import StoreItem, StoreItemVariant


class PublicStoreItemVariantSerializer(ModelSerializer[StoreItemVariant]):
    """Public serializer for StoreItemVariant - nested in store items.

    Only exposes id and name, not the item reference.
    """

    class Meta:
        model = StoreItemVariant
        fields = ("id", "name")


class PublicStoreItemSerializer(ModelSerializer[StoreItem]):
    """Public read-only serializer for StoreItem model.

    This serializer is used for the public store endpoint (/api/v2/store/items/).
    It does NOT expose sensitive fields like is_secret, secret_key, or is_ticket.
    """

    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    discount_factor = SerializerMethodField()
    num_available = SerializerMethodField()
    variants = PublicStoreItemVariantSerializer(many=True, read_only=True)

    def get_imagefile_original_url(self, obj: StoreItem) -> str | None:
        if not obj.imagefile_original:
            return None
        return str(self.context["request"].build_absolute_uri(obj.imagefile_original.url))

    def get_imagefile_thumbnail_url(self, obj: StoreItem) -> str | None:
        if not obj.imagefile_thumbnail:
            return None
        return str(self.context["request"].build_absolute_uri(obj.imagefile_thumbnail.url))

    def get_discount_factor(self, obj: StoreItem) -> float:
        return obj.get_discount_factor()

    def get_num_available(self, obj: StoreItem) -> int:
        return obj.num_available()

    class Meta:
        model = StoreItem
        fields = (
            "id",
            "event",
            "name",
            "description",
            "price",
            "max",
            "available",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "max_per_order",
            "sort_index",
            "discount_amount",
            "discount_percentage",
            "is_discount_available",
            "discount_factor",
            "num_available",
            "variants",
        )

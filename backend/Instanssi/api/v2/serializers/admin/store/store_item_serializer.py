from rest_framework.serializers import ModelSerializer, SerializerMethodField

from Instanssi.store.models import StoreItem, StoreItemVariant


class StoreItemVariantSerializer(ModelSerializer[StoreItemVariant]):
    class Meta:
        model = StoreItemVariant
        fields = ("id", "item", "name")
        read_only_fields = ("id",)


class StoreItemSerializer(ModelSerializer[StoreItem]):
    """Serializer for StoreItem model.

    Used for both public read access and staff CRUD operations.
    For public access, includes computed fields like num_available and discount_factor.
    """

    imagefile_original_url = SerializerMethodField()
    imagefile_thumbnail_url = SerializerMethodField()
    discount_factor = SerializerMethodField()
    num_available = SerializerMethodField()
    variants = StoreItemVariantSerializer(many=True, read_only=True)

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
            "imagefile_original",
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "max_per_order",
            "sort_index",
            "discount_amount",
            "discount_percentage",
            "is_discount_available",
            "discount_factor",
            "num_available",
            "is_ticket",
            "is_secret",
            "secret_key",
            "variants",
        )
        read_only_fields = (
            "id",
            "event",  # Set from URL, not request body
            "imagefile_original_url",
            "imagefile_thumbnail_url",
            "discount_factor",
            "num_available",
            "is_discount_available",
            "variants",
        )

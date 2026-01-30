from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from Instanssi.ext_blog.models import BlogEntry


class BlogEntrySerializer(ModelSerializer[BlogEntry]):
    """Serializer for staff - includes all fields.

    The user field is read-only and set automatically to the current user on create.
    """

    created_by = SerializerMethodField()

    def get_created_by(self, entry: BlogEntry) -> str:
        return entry.user.get_username() if entry.user else ""

    class Meta:
        model = BlogEntry
        fields = ("id", "user", "date", "title", "text", "public", "event", "created_by")
        read_only_fields = ("id", "user", "date", "created_by")

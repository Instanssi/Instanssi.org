from rest_framework.serializers import ModelSerializer

from Instanssi.ext_blog.models import BlogEntry


class PublicBlogEntrySerializer(ModelSerializer[BlogEntry]):
    """Serializer for public blog entries - excludes user, public, and created_by fields"""

    class Meta:
        model = BlogEntry
        fields = ("id", "date", "title", "text", "event")

from Instanssi.api.v2.serializers.admin.blog_entry import BlogEntrySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.ext_blog.models import BlogEntry


class BlogEntryViewSet(PermissionViewSet):
    """Staff viewset for managing blog entries."""

    queryset = BlogEntry.objects.all()
    serializer_class = BlogEntrySerializer  # type: ignore[assignment]
    ordering_fields = ("id", "user", "date")
    filterset_fields = ("user", "event")
    search_fields = ("title", "text")

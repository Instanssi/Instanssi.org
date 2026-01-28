from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter

from Instanssi.api.v2.serializers.public.blog_entry import PublicBlogEntrySerializer
from Instanssi.api.v2.utils.base import PublicReadOnlyViewSet
from Instanssi.ext_blog.models import BlogEntry


class PublicBlogEntryViewSet(PublicReadOnlyViewSet[BlogEntry]):
    """Public read-only endpoint for blog entries. Only public entries are shown."""

    serializer_class = PublicBlogEntrySerializer
    filter_backends = (OrderingFilter, SearchFilter, DjangoFilterBackend)
    ordering_fields = ("id", "date")
    search_fields = ("title", "text")
    filterset_fields = ("event",)

    def get_queryset(self) -> QuerySet[BlogEntry]:
        return BlogEntry.objects.filter(public=True)

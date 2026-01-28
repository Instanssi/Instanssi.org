from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.admin.blog_entry import BlogEntrySerializer
from Instanssi.api.v2.utils.base import PermissionViewSet
from Instanssi.ext_blog.models import BlogEntry


class BlogEntryViewSet(PermissionViewSet):
    queryset = BlogEntry.objects.all()
    serializer_class = BlogEntrySerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "user", "date")
    filterset_fields = ("user", "event")
    search_fields = ("title", "text")

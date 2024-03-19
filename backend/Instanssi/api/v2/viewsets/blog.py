from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.blog import AdminBlogSerializer
from Instanssi.api.v2.utils.base import AdminViewSet
from Instanssi.ext_blog.models import BlogEntry


class BlogViewSet(AdminViewSet):
    queryset = BlogEntry.objects.all()
    serializer_class = AdminBlogSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "user", "date")
    filterset_fields = ("user", "date", "event")
    search_fields = ("title", "text")

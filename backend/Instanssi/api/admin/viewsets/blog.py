from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.admin.serializers.blog import AdminBlogSerializer
from Instanssi.api.admin.viewsets.base import AdminViewSet
from Instanssi.ext_blog.models import BlogEntry


class AdminBlogViewSet(AdminViewSet):
    queryset = BlogEntry.objects.all()
    serializer_class = AdminBlogSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "user", "date")
    filterset_fields = ("user", "date", "event")

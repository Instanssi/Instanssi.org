from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import SAFE_METHODS
from rest_framework.request import Request
from rest_framework.serializers import BaseSerializer
from rest_framework.views import APIView

from Instanssi.api.v2.serializers.blog_entry import (
    BlogEntrySerializer,
    PublicBlogEntrySerializer,
)
from Instanssi.api.v2.utils.base import FullDjangoModelPermissions, PermissionViewSet
from Instanssi.ext_blog.models import BlogEntry


class PublicBlogEntryReadPermission(FullDjangoModelPermissions):
    """Allow read access to public blog entries for everyone, full permissions for staff."""

    def has_permission(self, request: Request, view: APIView) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request: Request, view: APIView, obj: BlogEntry) -> bool:
        if request.method in SAFE_METHODS and obj.public:
            return True
        return super().has_permission(request, view)


class BlogEntryViewSet(PermissionViewSet):
    queryset = BlogEntry.objects.all()
    serializer_class = BlogEntrySerializer  # type: ignore[assignment]
    pagination_class = LimitOffsetPagination
    permission_classes = [PublicBlogEntryReadPermission]
    filter_backends = (
        OrderingFilter,
        SearchFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "user", "date")
    filterset_fields = ("user", "event")
    search_fields = ("title", "text")

    def has_view_permissions(self) -> bool:
        return self.request.user.is_authenticated and self.request.user.has_perm("ext_blog.view_blogentry")

    def get_serializer_class(self) -> type[BaseSerializer[BlogEntry]]:  # type: ignore[override]
        """Use public serializer for non-staff users"""
        if self.has_view_permissions():
            return BlogEntrySerializer
        return PublicBlogEntrySerializer

    def get_queryset(self) -> QuerySet[BlogEntry]:
        """Filter blog entries - non-staff users only see public entries"""
        queryset = self.queryset
        if not self.has_view_permissions():
            queryset = queryset.filter(public=True)
        return queryset

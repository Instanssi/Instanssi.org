from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from rest_framework.pagination import LimitOffsetPagination

from Instanssi.api.v2.serializers.user import UserSerializer
from Instanssi.api.v2.utils.base import PermissionViewSet


class UserViewSet(PermissionViewSet):
    queryset = get_user_model().objects.all()
    serializer_class = UserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (
        OrderingFilter,
        DjangoFilterBackend,
    )
    ordering_fields = ("id", "username", "first_name", "last_name", "email")
    filterset_fields = ("email", "username")
    search_fields = ("username", "first_name", "last_name", "email")

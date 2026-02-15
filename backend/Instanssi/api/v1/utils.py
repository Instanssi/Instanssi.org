from typing import Any

from django.contrib.auth.models import Group
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.viewsets import GenericViewSet


class GroupBasePermission(BasePermission):
    group_name = ""

    def has_permission(self, request: Request, view: Any) -> bool:
        try:
            request.user.groups.get(name=self.group_name)
        except Group.DoesNotExist:
            return False
        return True


class ReadUpdateModelViewSet(RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet[Any]):
    pass


class ReadWriteUpdateModelViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet[Any]
):
    pass


class ReadWriteModelViewSet(CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[Any]):
    pass


class ReadWriteDeleteModelViewSet(
    CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[Any]
):
    pass


class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return request.method == "POST" or request.method in SAFE_METHODS or request.user.is_authenticated


class IsWriteOnly(BasePermission):
    def has_permission(self, request: Request, view: Any) -> bool:
        return request.method == "POST"


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet[Any]):
    pass

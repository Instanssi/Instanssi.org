from typing import Any, Generic, TypeVar

from django.contrib.auth.models import Group
from django.db.models import Model
from rest_framework.mixins import (
    CreateModelMixin,
    DestroyModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

_T = TypeVar("_T", bound=Model)


class GroupBasePermission(BasePermission):
    group_name = ""

    def has_permission(self, request: Request, view: APIView) -> bool:
        try:
            request.user.groups.get(name=self.group_name)
        except Group.DoesNotExist:
            return False
        return True


class ReadUpdateModelViewSet(
    RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet[_T], Generic[_T]
):
    pass


class ReadWriteUpdateModelViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, UpdateModelMixin, GenericViewSet[_T], Generic[_T]
):
    pass


class ReadWriteModelViewSet(
    CreateModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[_T], Generic[_T]
):
    pass


class ReadWriteDeleteModelViewSet(
    CreateModelMixin, DestroyModelMixin, RetrieveModelMixin, ListModelMixin, GenericViewSet[_T], Generic[_T]
):
    pass


class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method == "POST" or request.method in SAFE_METHODS or request.user.is_authenticated


class IsWriteOnly(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool:
        return request.method == "POST"


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet[_T], Generic[_T]):
    pass

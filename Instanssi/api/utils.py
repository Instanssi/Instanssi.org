# -*- coding: utf-8 -*-

from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.contrib.auth.models import Group


class GroupBasePermission(BasePermission):
    group_name = ""

    def has_permission(self, request, view):
        try:
            request.user.groups.get(name=self.group_name)
        except Group.DoesNotExist:
            return False
        return True


class CanUpdateScreenData(GroupBasePermission):
    group_name = "screen_update"


class ReadUpdateModelViewSet(RetrieveModelMixin,
                             ListModelMixin,
                             UpdateModelMixin,
                             GenericViewSet):
    pass


class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == 'POST' or
            request.method in SAFE_METHODS or
            request.user.is_authenticated()
        )


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet):
    pass

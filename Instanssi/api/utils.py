from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, ListModelMixin,\
    DestroyModelMixin
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


class ReadWriteUpdateModelViewSet(CreateModelMixin,
                                  RetrieveModelMixin,
                                  ListModelMixin,
                                  UpdateModelMixin,
                                  GenericViewSet):
    pass


class ReadWriteModelViewSet(CreateModelMixin,
                            RetrieveModelMixin,
                            ListModelMixin,
                            GenericViewSet):
    pass


class ReadWriteDeleteModelViewSet(CreateModelMixin,
                                  DestroyModelMixin,
                                  RetrieveModelMixin,
                                  ListModelMixin,
                                  GenericViewSet):
    pass


class IsAuthenticatedOrWriteOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method == 'POST' or
            request.method in SAFE_METHODS or
            request.user.is_authenticated
        )


class WriteOnlyModelViewSet(CreateModelMixin, GenericViewSet):
    pass

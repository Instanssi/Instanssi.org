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


class FilterMixin(object):
    @staticmethod
    def filter_by_event(queryset, request):
        event = request.query_params.get('event', None)
        return queryset.filter(event=event) if event else queryset

    @staticmethod
    def filter_by_compo(queryset, request):
        compo = request.query_params.get('compo', None)
        return queryset.filter(compo=compo) if compo else queryset

    @staticmethod
    def filter_by_competition(queryset, request):
        competition = request.query_params.get('competition', None)
        return queryset.filter(competition=competition) if competition else queryset

    @staticmethod
    def filter_by_lim_off(queryset, request):
        limit = int(request.query_params.get('limit', 100))
        offset = int(request.query_params.get('offset', 0))
        return queryset[offset:offset+limit]

    @staticmethod
    def order_by(queryset, request, default='id', whitelist=None):
        if not whitelist:
            whitelist = ['id', '-id']
        order_by = request.query_params.get('order_by', default)
        if order_by not in whitelist:
            return queryset.order_by(default)
        return queryset.order_by(order_by)

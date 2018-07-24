# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from django.contrib.auth.models import User, Group

from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend

from Instanssi.kompomaatti.models import (
    Event, Compo, Entry, CompetitionParticipation, Competition)
from Instanssi.ext_blog.models import BlogEntry
from .admin_serializers import (
    AdminEventSerializer, AdminCompoEntrySerializer, AdminCompoSerializer, AdminCompetitionSerializer,
    AdminCompetitionParticipationSerializer, AdminUserSerializer, AdminGroupSerializer, AdminBlogEntrySerializer)


class AdminUsersViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminUserSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'username')
    filter_fields = ('username',)


class AdminGroupsViewSet(ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminGroupSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'name')
    filter_fields = ('name',)


class AdminEventViewSet(ModelViewSet):
    queryset = Event.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminEventSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'name', 'date')
    filter_fields = ('name', 'date',)


class AdminCompoViewSet(ModelViewSet):
    queryset = Compo.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminCompoSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'event',)
    filter_fields = ('event',)


class AdminCompetitionViewSet(ModelViewSet):
    queryset = Competition.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminCompetitionSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'event',)
    filter_fields = ('event',)


class AdminCompoEntryViewSet(ModelViewSet):
    queryset = Entry.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminCompoEntrySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'compo',)
    filter_fields = ('compo',)


class AdminCompetitionParticipationViewSet(ModelViewSet):
    queryset = CompetitionParticipation.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminCompetitionParticipationSerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'competition',)
    filter_fields = ('competition',)


class AdminBlogEntryViewSet(ModelViewSet):
    queryset = BlogEntry.objects.all()
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = AdminBlogEntrySerializer
    pagination_class = LimitOffsetPagination
    filter_backends = (OrderingFilter, DjangoFilterBackend,)
    ordering_fields = ('id', 'user', 'event',)
    filter_fields = ('user', 'event',)

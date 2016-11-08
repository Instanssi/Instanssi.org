# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers
from .viewsets import EventViewSet, SongViewSet, CompetitionViewSet


router = routers.DefaultRouter()
router.register(r'events', EventViewSet)
router.register(r'songs', SongViewSet, base_name='songs')
router.register(r'competitions', CompetitionViewSet, base_name='competitions')

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^auth/', include('rest_framework.urls', namespace='rest_framework'))
]

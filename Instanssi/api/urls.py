# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.conf import settings
from rest_framework import routers
import oauth2_provider.views as oauth2_views
from .viewsets import EventViewSet, SongViewSet, CompetitionViewSet, CompoViewSet, ProgrammeEventViewSet,\
    SponsorViewSet, MessageViewSet, IRCMessageViewSet

# API Endpoints
router = routers.DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'songs', SongViewSet, base_name='songs')
router.register(r'competitions', CompetitionViewSet, base_name='competitions')
router.register(r'compos', CompoViewSet, base_name='compos')
router.register(r'programme_events', ProgrammeEventViewSet, base_name='programme_events')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'messages', MessageViewSet, base_name='messages')
router.register(r'irc_messages', IRCMessageViewSet, base_name='irc_messages')


# Base endpoints for OAuth2 authorization
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

# OAuth2 Application Management endpoints
if settings.DEBUG:
    oauth2_endpoint_views += [
        url(r'^applications/$', oauth2_views.ApplicationList.as_view(), name="list"),
        url(r'^applications/register/$', oauth2_views.ApplicationRegistration.as_view(), name="register"),
        url(r'^applications/(?P<pk>\d+)/$', oauth2_views.ApplicationDetail.as_view(), name="detail"),
        url(r'^applications/(?P<pk>\d+)/delete/$', oauth2_views.ApplicationDelete.as_view(), name="delete"),
        url(r'^applications/(?P<pk>\d+)/update/$', oauth2_views.ApplicationUpdate.as_view(), name="update"),
        url(r'^authorized-tokens/$', oauth2_views.AuthorizedTokensListView.as_view(), name="authorized-token-list"),
        url(r'^authorized-tokens/(?P<pk>\d+)/delete/$', oauth2_views.AuthorizedTokenDeleteView.as_view(),
            name="authorized-token-delete"),
    ]

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^oauth2/', include(oauth2_endpoint_views, namespace="oauth2_provider")),
]

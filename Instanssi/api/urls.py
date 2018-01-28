# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers
import oauth2_provider.views as oauth2_views
from .viewsets import EventViewSet, SongViewSet, CompetitionViewSet, CompoViewSet, ProgrammeEventViewSet,\
    SponsorViewSet, MessageViewSet, IRCMessageViewSet, StoreItemViewSet, StoreTransactionViewSet,\
    CompoEntryViewSet, CompetitionParticipationViewSet, CurrentUserViewSet, UserCompoEntryViewSet,\
    UserCompetitionParticipationViewSet

# API Endpoints
router = routers.DefaultRouter()
router.register(r'events', EventViewSet, base_name='events')
router.register(r'songs', SongViewSet, base_name='songs')
router.register(r'competitions', CompetitionViewSet, base_name='competitions')
router.register(r'competition_participations', CompetitionParticipationViewSet, base_name='competition_participations')
router.register(r'user_participations', UserCompetitionParticipationViewSet, base_name='user_participations')
router.register(r'compos', CompoViewSet, base_name='compos')
router.register(r'compo_entries', CompoEntryViewSet, base_name='compo_entries')
router.register(r'user_entries', UserCompoEntryViewSet, base_name='user_entries')
router.register(r'programme_events', ProgrammeEventViewSet, base_name='programme_events')
router.register(r'sponsors', SponsorViewSet, base_name='sponsors')
router.register(r'messages', MessageViewSet, base_name='messages')
router.register(r'irc_messages', IRCMessageViewSet, base_name='irc_messages')
router.register(r'store_items', StoreItemViewSet, base_name='store_items')
router.register(r'store_transaction', StoreTransactionViewSet, base_name='store_transaction')
router.register(r'current_user', CurrentUserViewSet, base_name='current_user')


# Base endpoints for OAuth2 authorization
oauth2_endpoint_views = [
    url(r'^authorize/$', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r'^token/$', oauth2_views.TokenView.as_view(), name="token"),
    url(r'^revoke-token/$', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^oauth2/', include(oauth2_endpoint_views, namespace="oauth2_provider")),
]

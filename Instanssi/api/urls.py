# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from rest_framework import routers
import oauth2_provider.views as oauth2_views
from .viewsets import (
    EventViewSet, SongViewSet, CompetitionViewSet, CompoViewSet, ProgrammeEventViewSet,
    SponsorViewSet, MessageViewSet, IRCMessageViewSet, StoreItemViewSet, StoreTransactionViewSet,
    CompoEntryViewSet, CompetitionParticipationViewSet, CurrentUserViewSet, UserCompoEntryViewSet,
    UserCompetitionParticipationViewSet, VoteCodeRequestViewSet, TicketVoteCodeViewSet, VoteGroupViewSet)
from .admin_viewsets import (
    AdminEventViewSet, AdminCompoViewSet, AdminCompetitionParticipationViewSet, AdminCompetitionViewSet,
    AdminCompoEntryViewSet, AdminUsersViewSet, AdminGroupsViewSet, AdminBlogEntryViewSet, AdminUploadedFileViewSet)

app_name = "api"


class InstanssiAPIRoot(routers.APIRootView):
    """
    This is the v1 Instanssi API. Most things work only for logged in users.
    """
    pass


class CustomRouter(routers.DefaultRouter):
    APIRootView = InstanssiAPIRoot


# API Endpoints
router = CustomRouter()
router.register('events', EventViewSet, base_name='events')
router.register('songs', SongViewSet, base_name='songs')
router.register('competitions', CompetitionViewSet, base_name='competitions')
router.register('competition_participations', CompetitionParticipationViewSet, base_name='competition_participations')
router.register('user_participations', UserCompetitionParticipationViewSet, base_name='user_participations')
router.register('compos', CompoViewSet, base_name='compos')
router.register('compo_entries', CompoEntryViewSet, base_name='compo_entries')
router.register('user_entries', UserCompoEntryViewSet, base_name='user_entries')
router.register('programme_events', ProgrammeEventViewSet, base_name='programme_events')
router.register('sponsors', SponsorViewSet, base_name='sponsors')
router.register('messages', MessageViewSet, base_name='messages')
router.register('irc_messages', IRCMessageViewSet, base_name='irc_messages')
router.register('store_items', StoreItemViewSet, base_name='store_items')
router.register('store_transaction', StoreTransactionViewSet, base_name='store_transaction')
router.register('current_user', CurrentUserViewSet, base_name='current_user')
router.register('user_vote_codes', TicketVoteCodeViewSet, base_name='user_vote_codes')
router.register('user_vote_code_requests', VoteCodeRequestViewSet, base_name='user_vote_code_requests')
router.register('user_votes', VoteGroupViewSet, base_name='user_votes')

router.register('admin/groups', AdminGroupsViewSet, base_name='admin_groups')
router.register('admin/users', AdminUsersViewSet, base_name='admin_users')
router.register('admin/events', AdminEventViewSet, base_name='admin_events')
router.register('admin/compos', AdminCompoViewSet, base_name='admin_compos')
router.register('admin/compo_entries', AdminCompoEntryViewSet, base_name='admin_compo_entries')
router.register('admin/competitions', AdminCompetitionViewSet, base_name='admin_competitions')
router.register('admin/competition_participations', AdminCompetitionParticipationViewSet,
                base_name='admin_competition_participations')
router.register('admin/blog_entries', AdminBlogEntryViewSet, base_name='admin_blog_entries')
router.register('admin/uploaded_files', AdminUploadedFileViewSet, base_name='admin_uploaded_files')

# Base endpoints for OAuth2 authorization
oauth2_endpoint_views = [
    url('authorize/', oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url('token/', oauth2_views.TokenView.as_view(), name="token"),
    url('revoke-token/', oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [
    url('', include(router.urls)),
    url('oauth2/', include((oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider")),
]

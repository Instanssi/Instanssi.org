import oauth2_provider.views as oauth2_views
from django.conf.urls import include, url
from rest_framework import routers

from .viewsets import (
    CompetitionParticipationViewSet,
    CompetitionViewSet,
    CompoEntryViewSet,
    CompoViewSet,
    CurrentUserViewSet,
    EventViewSet,
    IRCMessageViewSet,
    MessageViewSet,
    ProgrammeEventViewSet,
    SongViewSet,
    SponsorViewSet,
    StoreItemViewSet,
    StoreTransactionViewSet,
    TicketVoteCodeViewSet,
    UserCompetitionParticipationViewSet,
    UserCompoEntryViewSet,
    VoteCodeRequestViewSet,
    VoteGroupViewSet,
)

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
router.register(r"events", EventViewSet, basename="events")
router.register(r"songs", SongViewSet, basename="songs")
router.register(r"competitions", CompetitionViewSet, basename="competitions")
router.register(
    r"competition_participations",
    CompetitionParticipationViewSet,
    basename="competition_participations",
)
router.register(r"user_participations", UserCompetitionParticipationViewSet, basename="user_participations")
router.register(r"compos", CompoViewSet, basename="compos")
router.register(r"compo_entries", CompoEntryViewSet, basename="compo_entries")
router.register(r"user_entries", UserCompoEntryViewSet, basename="user_entries")
router.register(r"programme_events", ProgrammeEventViewSet, basename="programme_events")
router.register(r"sponsors", SponsorViewSet, basename="sponsors")
router.register(r"messages", MessageViewSet, basename="messages")
router.register(r"irc_messages", IRCMessageViewSet, basename="irc_messages")
router.register(r"store_items", StoreItemViewSet, basename="store_items")
router.register(r"store_transaction", StoreTransactionViewSet, basename="store_transaction")
router.register(r"current_user", CurrentUserViewSet, basename="current_user")
router.register(r"user_vote_codes", TicketVoteCodeViewSet, basename="user_vote_codes")
router.register(r"user_vote_code_requests", VoteCodeRequestViewSet, basename="user_vote_code_requests")
router.register(r"user_votes", VoteGroupViewSet, basename="user_votes")


# Base endpoints for OAuth2 authorization
oauth2_endpoint_views = [
    url(r"^authorize/$", oauth2_views.AuthorizationView.as_view(), name="authorize"),
    url(r"^token/$", oauth2_views.TokenView.as_view(), name="token"),
    url(r"^revoke-token/$", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [
    url(r"^", include(router.urls)),
    url(
        r"^oauth2/",
        include((oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider"),
    ),
]

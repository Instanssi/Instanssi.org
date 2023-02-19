import oauth2_provider.views as oauth2_views
from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from .admin.viewsets.kompomaatti import (
    AdminCompoEntryViewSet,
    AdminCompoViewSet,
    AdminEventViewSet,
)
from .viewsets.kompomaatti import (
    CompetitionParticipationViewSet,
    CompetitionViewSet,
    CompoEntryViewSet,
    CompoViewSet,
    EventViewSet,
    TicketVoteCodeViewSet,
    UserCompetitionParticipationViewSet,
    UserCompoEntryViewSet,
    VoteCodeRequestViewSet,
    VoteGroupViewSet,
)
from .viewsets.programme import ProgrammeEventViewSet
from .viewsets.screenshow import (
    IRCMessageViewSet,
    MessageViewSet,
    SongViewSet,
    SponsorViewSet,
)
from .viewsets.store import StoreItemViewSet, StoreTransactionViewSet
from .viewsets.user import CurrentUserViewSet

app_name = "api"


class InstanssiAPIRoot(routers.APIRootView):
    """
    This is the v1 Instanssi API. Most things work only for logged in users.
    """

    pass


class CustomRouter(routers.DefaultRouter):
    APIRootView = InstanssiAPIRoot


router = CustomRouter()

# Public API
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

# Admin API (requires admin privileges)
router.register("admin/events", AdminEventViewSet, basename="admin_events")
router.register("admin/compos", AdminCompoViewSet, basename="admin_compos")
router.register("admin/compo_entries", AdminCompoEntryViewSet, basename="admin_compo_entries")

# Oauth2 entrypoints for applications
oauth2_endpoint_views = [
    path("authorize/", oauth2_views.AuthorizationView.as_view(), name="authorize"),
    path("token/", oauth2_views.TokenView.as_view(), name="token"),
    path("revoke-token/", oauth2_views.RevokeTokenView.as_view(), name="revoke-token"),
]

urlpatterns = [
    path("", include(router.urls)),
    path("oauth2/", include((oauth2_endpoint_views, "oauth2_provider"), namespace="oauth2_provider")),
]

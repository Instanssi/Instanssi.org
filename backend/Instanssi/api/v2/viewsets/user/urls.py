from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.user.kompomaatti.user_competition_participations import (
    UserCompetitionParticipationViewSet,
)
from Instanssi.api.v2.viewsets.user.kompomaatti.user_compo_entries import (
    UserCompoEntryViewSet,
)
from Instanssi.api.v2.viewsets.user.kompomaatti.user_ticket_vote_codes import (
    UserTicketVoteCodeViewSet,
)
from Instanssi.api.v2.viewsets.user.kompomaatti.user_vote_code_requests import (
    UserVoteCodeRequestViewSet,
)
from Instanssi.api.v2.viewsets.user.kompomaatti.user_vote_groups import (
    UserVoteGroupViewSet,
)
from Instanssi.api.v2.viewsets.user.tokens import UserTokenViewSet
from Instanssi.api.v2.viewsets.user.user_info import UserInfoViewSet

# /api/v2/user_info/
user_info_view = UserInfoViewSet.as_view({"get": "retrieve", "patch": "partial_update"})

# /api/v2/tokens/
tokens_router = routers.SimpleRouter()
tokens_router.register("tokens", UserTokenViewSet, basename="user_tokens")

# /api/v2/event/<event_pk>/user/kompomaatti/...
kompomaatti_router = routers.SimpleRouter()
kompomaatti_router.register("entries", UserCompoEntryViewSet, basename="event_user_kompomaatti_entries")
kompomaatti_router.register(
    "participations", UserCompetitionParticipationViewSet, basename="event_user_kompomaatti_participations"
)
kompomaatti_router.register(
    "vote_code_requests", UserVoteCodeRequestViewSet, basename="event_user_kompomaatti_vote_code_requests"
)
kompomaatti_router.register(
    "ticket_vote_codes", UserTicketVoteCodeViewSet, basename="event_user_kompomaatti_ticket_vote_codes"
)
kompomaatti_router.register("votes", UserVoteGroupViewSet, basename="event_user_kompomaatti_votes")

urlpatterns: list[URLPattern | URLResolver] = [
    path("user_info/", user_info_view, name="user_info"),
    path("", include(tokens_router.urls)),
    path("event/<int:event_pk>/user/kompomaatti/", include(kompomaatti_router.urls)),
]

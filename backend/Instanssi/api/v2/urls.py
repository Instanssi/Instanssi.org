from django.conf import settings
from django.urls import include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.auth.login import LoginViewSet
from Instanssi.api.v2.viewsets.auth.logout import LogoutViewSet
from Instanssi.api.v2.viewsets.auth.social_auth import SocialAuthUrlsViewSet
from Instanssi.api.v2.viewsets.blog_entries import BlogEntryViewSet
from Instanssi.api.v2.viewsets.events import EventViewSet
from Instanssi.api.v2.viewsets.kompomaatti.competition_participations import (
    CompetitionParticipationViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.competitions import CompetitionViewSet
from Instanssi.api.v2.viewsets.kompomaatti.compo_entries import CompoEntryViewSet
from Instanssi.api.v2.viewsets.kompomaatti.compos import CompoViewSet
from Instanssi.api.v2.viewsets.kompomaatti.ticket_vote_codes import (
    TicketVoteCodeViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.user_compo_entries import (
    UserCompoEntryViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.vote_code_requests import (
    VoteCodeRequestViewSet,
)
from Instanssi.api.v2.viewsets.user.user_info import UserInfoViewSet
from Instanssi.api.v2.viewsets.users import UserViewSet

app_name = "api-v2"


class InstanssiV2APIRoot(routers.APIRootView):
    """Instanssi v2 API"""

    pass


class V2CustomRouter(routers.DefaultRouter):
    APIRootView = InstanssiV2APIRoot


router = V2CustomRouter()

# Generic data API
# This should contain full read-write API for all data along with permission checking
router.register("events", EventViewSet, basename="events")
router.register("users", UserViewSet, basename="users")
router.register("blog_entries", BlogEntryViewSet, basename="blog_entries")

# Authentication API
router.register("auth/social_urls", SocialAuthUrlsViewSet, basename="auth_social_urls")
router.register("auth/login", LoginViewSet, basename="auth_login")
router.register("auth/logout", LogoutViewSet, basename="auth_logout")

# Self data API
# This should only allow access to data belonging to the current user
router.register("user_info", UserInfoViewSet, basename="user_info")

# Kompomaatti API nested under events
# These endpoints use FullDjangoModelPermissions for access control
# Nested routers: /api/v2/event/<event_pk>/kompomaatti/...
kompomaatti_router = routers.SimpleRouter()
kompomaatti_router.register("compos", CompoViewSet, basename="event_kompomaatti_compos")
kompomaatti_router.register("entries", CompoEntryViewSet, basename="event_kompomaatti_entries")
kompomaatti_router.register("competitions", CompetitionViewSet, basename="event_kompomaatti_competitions")
kompomaatti_router.register(
    "competition_participations",
    CompetitionParticipationViewSet,
    basename="event_kompomaatti_competition_participations",
)
kompomaatti_router.register(
    "vote_code_requests", VoteCodeRequestViewSet, basename="event_kompomaatti_vote_code_requests"
)
kompomaatti_router.register(
    "ticket_vote_codes", TicketVoteCodeViewSet, basename="event_kompomaatti_ticket_vote_codes"
)

# User-specific kompomaatti API nested under events
# These endpoints are for user's own entries and require authentication
# Nested routers: /api/v2/event/<event_pk>/user/kompomaatti/...
user_kompomaatti_router = routers.SimpleRouter()
user_kompomaatti_router.register("entries", UserCompoEntryViewSet, basename="event_user_kompomaatti_entries")

urlpatterns = []
if settings.DEBUG:
    from drf_spectacular.views import (
        SpectacularAPIView,
        SpectacularRedocView,
        SpectacularSwaggerView,
    )

    urlpatterns += [
        path("openapi/", SpectacularAPIView.as_view(), name="openapi"),
        path(
            "openapi/swagger-ui/",
            SpectacularSwaggerView.as_view(url_name="api-v2:openapi"),
            name="swagger-ui",
        ),
        path("openapi/redoc/", SpectacularRedocView.as_view(url_name="api-v2:openapi"), name="redoc"),
    ]

urlpatterns += [
    # Nested kompomaatti routes under events
    path("event/<int:event_pk>/kompomaatti/", include(kompomaatti_router.urls)),
    # User-specific kompomaatti routes under events
    path("event/<int:event_pk>/user/kompomaatti/", include(user_kompomaatti_router.urls)),
    # Main routes
    path("", include(router.urls)),
]

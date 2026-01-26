from typing import Any

from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.admin import UploadedFileViewSet
from Instanssi.api.v2.viewsets.arkisto import (
    OtherVideoCategoryViewSet,
    OtherVideoViewSet,
)
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
from Instanssi.api.v2.viewsets.kompomaatti.user_competition_participations import (
    UserCompetitionParticipationViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.user_compo_entries import (
    UserCompoEntryViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.user_ticket_vote_codes import (
    UserTicketVoteCodeViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.user_vote_code_requests import (
    UserVoteCodeRequestViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.user_vote_groups import (
    UserVoteGroupViewSet,
)
from Instanssi.api.v2.viewsets.kompomaatti.vote_code_requests import (
    VoteCodeRequestViewSet,
)
from Instanssi.api.v2.viewsets.programme import ProgrammeEventViewSet
from Instanssi.api.v2.viewsets.store import (
    PublicStoreItemViewSet,
    PublicStoreTransactionCheckoutViewSet,
    ReceiptViewSet,
    StoreItemVariantViewSet,
    StoreItemViewSet,
    StoreTransactionViewSet,
    TransactionItemViewSet,
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
user_kompomaatti_router.register(
    "participations", UserCompetitionParticipationViewSet, basename="event_user_kompomaatti_participations"
)
user_kompomaatti_router.register(
    "vote_code_requests", UserVoteCodeRequestViewSet, basename="event_user_kompomaatti_vote_code_requests"
)
user_kompomaatti_router.register(
    "ticket_vote_codes", UserTicketVoteCodeViewSet, basename="event_user_kompomaatti_ticket_vote_codes"
)
user_kompomaatti_router.register("votes", UserVoteGroupViewSet, basename="event_user_kompomaatti_votes")

# Store API nested under events
# Nested routers: /api/v2/event/<event_pk>/store/...
store_router = routers.SimpleRouter()
store_router.register("items", StoreItemViewSet, basename="event_store_items")
store_router.register("item_variants", StoreItemVariantViewSet, basename="event_store_item_variants")
store_router.register("transactions", StoreTransactionViewSet, basename="event_store_transactions")
store_router.register("transaction_items", TransactionItemViewSet, basename="event_store_transaction_items")
store_router.register("receipts", ReceiptViewSet, basename="event_store_receipts")

# Public store API (no authentication required)
# /api/v2/store/items/ - List available store items
# /api/v2/store/checkout/ - Create store transaction
public_store_router = routers.SimpleRouter()
public_store_router.register("items", PublicStoreItemViewSet, basename="store_items")
public_store_router.register("checkout", PublicStoreTransactionCheckoutViewSet, basename="store_checkout")

# Programme API nested under events
# Nested routers: /api/v2/event/<event_pk>/programme/...
programme_router = routers.SimpleRouter()
programme_router.register("events", ProgrammeEventViewSet, basename="event_programme_events")

# Archive API nested under events
# Nested routers: /api/v2/event/<event_pk>/archive/...
archive_router = routers.SimpleRouter()
archive_router.register(
    "video_categories", OtherVideoCategoryViewSet, basename="event_archive_video_categories"
)
archive_router.register("videos", OtherVideoViewSet, basename="event_archive_videos")

# Uploads API nested under events (staff-only)
# Nested routers: /api/v2/event/<event_pk>/uploads/...
uploads_router = routers.SimpleRouter()
uploads_router.register("files", UploadedFileViewSet, basename="event_uploads")

urlpatterns: list[URLPattern | URLResolver] = []
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
    # Nested store routes under events (staff access)
    path("event/<int:event_pk>/store/", include(store_router.urls)),
    # Nested programme routes under events
    path("event/<int:event_pk>/programme/", include(programme_router.urls)),
    # Nested archive routes under events
    path("event/<int:event_pk>/archive/", include(archive_router.urls)),
    # Nested uploads routes under events (staff-only)
    path("event/<int:event_pk>/uploads/", include(uploads_router.urls)),
    # Public store checkout
    path("store/", include(public_store_router.urls)),
    # Main routes
    path("", include(router.urls)),
]

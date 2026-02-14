from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.public import (
    PublicBlogEntryViewSet,
    PublicCompetitionParticipationViewSet,
    PublicCompetitionViewSet,
    PublicCompoEntryViewSet,
    PublicCompoViewSet,
    PublicEventViewSet,
    PublicOtherVideoCategoryViewSet,
    PublicOtherVideoViewSet,
    PublicProgramEventViewSet,
)
from Instanssi.api.v2.viewsets.public.notifications import VapidPublicKeyView
from Instanssi.api.v2.viewsets.public.store.public_store_items import (
    PublicStoreItemViewSet,
)
from Instanssi.api.v2.viewsets.public.store.public_store_transaction_checkout import (
    PublicStoreTransactionCheckoutViewSet,
)

# /api/v2/public/ - Top-level public endpoints
public_router = routers.SimpleRouter()
public_router.register("events", PublicEventViewSet, basename="public_events")
public_router.register("blog_entries", PublicBlogEntryViewSet, basename="public_blog_entries")

# /api/v2/public/event/<event_pk>/kompomaatti/...
kompomaatti_router = routers.SimpleRouter()
kompomaatti_router.register("compos", PublicCompoViewSet, basename="public_kompomaatti_compos")
kompomaatti_router.register("entries", PublicCompoEntryViewSet, basename="public_kompomaatti_entries")
kompomaatti_router.register(
    "competitions", PublicCompetitionViewSet, basename="public_kompomaatti_competitions"
)
kompomaatti_router.register(
    "competition_participations",
    PublicCompetitionParticipationViewSet,
    basename="public_kompomaatti_competition_participations",
)

# /api/v2/public/event/<event_pk>/program/...
program_router = routers.SimpleRouter()
program_router.register("events", PublicProgramEventViewSet, basename="public_program_events")

# /api/v2/public/event/<event_pk>/archive/...
archive_router = routers.SimpleRouter()
archive_router.register(
    "video_categories", PublicOtherVideoCategoryViewSet, basename="public_archive_video_categories"
)
archive_router.register("videos", PublicOtherVideoViewSet, basename="public_archive_videos")

# /api/v2/public/store/...
store_router = routers.SimpleRouter()
store_router.register("items", PublicStoreItemViewSet, basename="public_store_items")
store_router.register("checkout", PublicStoreTransactionCheckoutViewSet, basename="public_store_checkout")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(public_router.urls)),
    path(
        "notifications/vapid-key/",
        VapidPublicKeyView.as_view(),
        name="public_notifications_vapid_key",
    ),
    path("event/<int:event_pk>/kompomaatti/", include(kompomaatti_router.urls)),
    path("event/<int:event_pk>/program/", include(program_router.urls)),
    path("event/<int:event_pk>/archive/", include(archive_router.urls)),
    path("store/", include(store_router.urls)),
]

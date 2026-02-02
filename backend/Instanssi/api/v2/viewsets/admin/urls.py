from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.admin.arkisto import (
    ArchiverViewSet,
    OtherVideoCategoryViewSet,
    OtherVideoViewSet,
)
from Instanssi.api.v2.viewsets.admin.auditlog import AuditLogViewSet
from Instanssi.api.v2.viewsets.admin.blog_entries import BlogEntryViewSet
from Instanssi.api.v2.viewsets.admin.events import EventViewSet
from Instanssi.api.v2.viewsets.admin.kompomaatti.competition_participations import (
    CompetitionParticipationViewSet,
)
from Instanssi.api.v2.viewsets.admin.kompomaatti.competitions import CompetitionViewSet
from Instanssi.api.v2.viewsets.admin.kompomaatti.compo_entries import CompoEntryViewSet
from Instanssi.api.v2.viewsets.admin.kompomaatti.compos import CompoViewSet
from Instanssi.api.v2.viewsets.admin.kompomaatti.ticket_vote_codes import (
    TicketVoteCodeViewSet,
)
from Instanssi.api.v2.viewsets.admin.kompomaatti.vote_code_requests import (
    VoteCodeRequestViewSet,
)
from Instanssi.api.v2.viewsets.admin.program import ProgramEventViewSet
from Instanssi.api.v2.viewsets.admin.store.receipts import ReceiptViewSet
from Instanssi.api.v2.viewsets.admin.store.store_item_variants import (
    StoreItemVariantViewSet,
)
from Instanssi.api.v2.viewsets.admin.store.store_items import StoreItemViewSet
from Instanssi.api.v2.viewsets.admin.store.store_transactions import (
    StoreTransactionViewSet,
)
from Instanssi.api.v2.viewsets.admin.store.transaction_items import (
    TransactionItemViewSet,
)
from Instanssi.api.v2.viewsets.admin.uploaded_files import UploadedFileViewSet
from Instanssi.api.v2.viewsets.admin.users import UserViewSet

# /api/v2/admin/ - Top-level admin endpoints
admin_router = routers.SimpleRouter()
admin_router.register("auditlog", AuditLogViewSet, basename="admin_auditlog")
admin_router.register("blog", BlogEntryViewSet, basename="admin_blog")
admin_router.register("events", EventViewSet, basename="admin_events")
admin_router.register("users", UserViewSet, basename="admin_users")

# /api/v2/admin/event/<event_pk>/kompomaatti/...
kompomaatti_router = routers.SimpleRouter()
kompomaatti_router.register("compos", CompoViewSet, basename="admin_kompomaatti_compos")
kompomaatti_router.register("entries", CompoEntryViewSet, basename="admin_kompomaatti_entries")
kompomaatti_router.register("competitions", CompetitionViewSet, basename="admin_kompomaatti_competitions")
kompomaatti_router.register(
    "competition_participations",
    CompetitionParticipationViewSet,
    basename="admin_kompomaatti_competition_participations",
)
kompomaatti_router.register(
    "vote_code_requests", VoteCodeRequestViewSet, basename="admin_kompomaatti_vote_code_requests"
)
kompomaatti_router.register(
    "ticket_vote_codes", TicketVoteCodeViewSet, basename="admin_kompomaatti_ticket_vote_codes"
)

# /api/v2/admin/event/<event_pk>/store/...
store_router = routers.SimpleRouter()
store_router.register("items", StoreItemViewSet, basename="admin_store_items")
store_router.register("item_variants", StoreItemVariantViewSet, basename="admin_store_item_variants")
store_router.register("transactions", StoreTransactionViewSet, basename="admin_store_transactions")
store_router.register("transaction_items", TransactionItemViewSet, basename="admin_store_transaction_items")
store_router.register("receipts", ReceiptViewSet, basename="admin_store_receipts")

# /api/v2/admin/event/<event_pk>/program/...
program_router = routers.SimpleRouter()
program_router.register("events", ProgramEventViewSet, basename="admin_program_events")

# /api/v2/admin/event/<event_pk>/arkisto/...
arkisto_router = routers.SimpleRouter()
arkisto_router.register("archiver", ArchiverViewSet, basename="admin_arkisto_archiver")
arkisto_router.register(
    "video_categories", OtherVideoCategoryViewSet, basename="admin_arkisto_video_categories"
)
arkisto_router.register("videos", OtherVideoViewSet, basename="admin_arkisto_videos")

# /api/v2/admin/event/<event_pk>/uploads/...
uploads_router = routers.SimpleRouter()
uploads_router.register("files", UploadedFileViewSet, basename="admin_uploads")

urlpatterns: list[URLPattern | URLResolver] = [
    path("", include(admin_router.urls)),
    path("event/<int:event_pk>/kompomaatti/", include(kompomaatti_router.urls)),
    path("event/<int:event_pk>/store/", include(store_router.urls)),
    path("event/<int:event_pk>/program/", include(program_router.urls)),
    path("event/<int:event_pk>/arkisto/", include(arkisto_router.urls)),
    path("event/<int:event_pk>/uploads/", include(uploads_router.urls)),
]

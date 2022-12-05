from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("", include("social_django.urls", namespace="social")),
    path("api/v1/", include("Instanssi.api.urls", namespace="api")),
    path("2022/", include("Instanssi.main2022.urls", namespace="main2022")),
    path("manage/events/", include("Instanssi.admin_events.urls", namespace="manage-events")),
    path("manage/users/", include("Instanssi.admin_users.urls", namespace="manage-users")),
    path("manage/profile/", include("Instanssi.admin_profile.urls", namespace="manage-profile")),
    path("manage/utils/", include("Instanssi.admin_utils.urls", namespace="manage-utils")),
    path("manage/store/", include("Instanssi.admin_store.urls", namespace="manage-store")),
    path(
        "manage/<int:selected_event_id>/",
        include("Instanssi.admin_events_overview.urls", namespace="manage-overview"),
    ),
    path(
        "manage/<int:selected_event_id>/files/",
        include("Instanssi.admin_upload.urls", namespace="manage-uploads"),
    ),
    path(
        "manage/<int:selected_event_id>/blog/",
        include("Instanssi.admin_blog.urls", namespace="manage-blog"),
    ),
    path(
        "manage/<int:selected_event_id>/arkisto/",
        include("Instanssi.admin_arkisto.urls", namespace="manage-arkisto"),
    ),
    path(
        "manage/<int:selected_event_id>/slides/",
        include("Instanssi.admin_slides.urls", namespace="manage-slides"),
    ),
    path(
        "manage/<int:selected_event_id>/screenshow/",
        include("Instanssi.admin_screenshow.urls", namespace="manage-screenshow"),
    ),
    path(
        "manage/<int:selected_event_id>/kompomaatti/",
        include("Instanssi.admin_kompomaatti.urls", namespace="manage-kompomaatti"),
    ),
    path(
        "manage/<int:selected_event_id>/programme/",
        include("Instanssi.admin_programme.urls", namespace="manage-programme"),
    ),
    path("manage/", include("Instanssi.admin_base.urls", namespace="manage-base")),
    path("users/", include("Instanssi.users.urls", namespace="users")),
    path("blog/", include("Instanssi.ext_blog.urls", namespace="ext-blog")),
    path("arkisto/", include("Instanssi.arkisto.urls", namespace="archive")),
    path("kompomaatti/", include("Instanssi.kompomaatti.urls", namespace="km")),
    path("screen/", include("Instanssi.screenshow.urls", namespace="screen")),
    path("store/", include("Instanssi.store.urls", namespace="store")),
    path("infodesk/", include("Instanssi.infodesk.urls", namespace="infodesk")),
    path("", RedirectView.as_view(url=reverse_lazy("main2022:index")), name="root-index"),
]

# Add admin panel link if debug mode is on
if settings.DEBUG or settings.ADMIN:
    admin.autodiscover()
    urlpatterns += [
        path("admin/", admin.site.urls),
    ]

if settings.DEBUG:
    # Serve media files through static.serve when running in debug mode
    urlpatterns += [
        url(r"^uploads/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, reverse_lazy
from django.views.generic import RedirectView
from django.views.static import serve

urlpatterns = [
    path("", include("social_django.urls", namespace="social")),
    path("qr/", include("qr_code.urls", namespace="qr_code")),
    path("api/v1/", include("Instanssi.api.v1.urls", namespace="api")),
    path("api/v2/", include("Instanssi.api.v2.urls", namespace="api-v2")),
    path("2024/", include("Instanssi.main2024.urls", namespace="main2024")),
    path("2026/", include("Instanssi.main2026.urls", namespace="main2026")),
    path("users/", include("Instanssi.users.urls", namespace="users")),
    path("blog/", include("Instanssi.ext_blog.urls", namespace="ext-blog")),
    path("arkisto/", include("Instanssi.arkisto.urls", namespace="archive")),
    path("kompomaatti/", include("Instanssi.kompomaatti.urls", namespace="km")),
    path("management/", include("Instanssi.management.urls", namespace="management")),
    path("store/", include("Instanssi.store.urls", namespace="store")),
    path("infodesk/", include("Instanssi.infodesk.urls", namespace="infodesk")),
    path("", RedirectView.as_view(url=reverse_lazy("main2026:index")), name="root-index"),
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
        path("uploads/<path:path>", serve, {"document_root": settings.MEDIA_ROOT}),
    ]

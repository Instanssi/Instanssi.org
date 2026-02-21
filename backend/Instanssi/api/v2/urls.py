from django.conf import settings
from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

app_name = "api-v2"


class InstanssiV2APIRoot(routers.APIRootView):
    """Instanssi v2 API"""

    pass


class V2CustomRouter(routers.DefaultRouter):
    APIRootView = InstanssiV2APIRoot


router = V2CustomRouter()

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
    path("admin/", include("Instanssi.api.v2.viewsets.admin.urls")),
    path("public/", include("Instanssi.api.v2.viewsets.public.urls")),
    path("", include("Instanssi.api.v2.viewsets.user.urls")),
    # API root
    path("", include(router.urls)),
]

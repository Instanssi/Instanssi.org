from django.conf import settings
from django.urls import include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.auth.login import LoginViewSet
from Instanssi.api.v2.viewsets.auth.logout import LogoutViewSet
from Instanssi.api.v2.viewsets.auth.social_auth import SocialAuthUrlsViewSet
from Instanssi.api.v2.viewsets.blog_entries import BlogEntryViewSet
from Instanssi.api.v2.viewsets.events import EventViewSet
from Instanssi.api.v2.viewsets.user.user_compo_entry import UserCompoEntryViewSet
from Instanssi.api.v2.viewsets.user.user_info import UserInfoViewSet

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
router.register("blog_entries", BlogEntryViewSet, basename="blog_entries")

# Authentication API
router.register("auth/social_urls", SocialAuthUrlsViewSet, basename="auth_social_urls")
router.register("auth/login", LoginViewSet, basename="auth_login")
router.register("auth/logout", LogoutViewSet, basename="auth_logout")

# Self data API
# This should only allow access to data belonging to the current user
router.register("user_info", UserInfoViewSet, basename="user_info")
router.register("user_compo_entries", UserCompoEntryViewSet, basename="user_compo_entries")

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
    path("", include(router.urls)),
]

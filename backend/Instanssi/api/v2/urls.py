from django.urls import include, path
from django.conf import settings
from rest_framework import routers

from Instanssi.api.v2.viewsets.auth.login import LoginViewSet
from Instanssi.api.v2.viewsets.auth.logout import LogoutViewSet
from Instanssi.api.v2.viewsets.auth.social_auth import BeginSocialAuthViewSet
from Instanssi.api.v2.viewsets.self.user import UserDataViewSet
from Instanssi.api.v2.viewsets.blog import BlogViewSet
from Instanssi.api.v2.viewsets.events import EventViewSet

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
router.register("blog", BlogViewSet, basename="blog")

# Authentication API
router.register("auth/social/begin", BeginSocialAuthViewSet, basename="auth_begin_social")
router.register("auth/login", LoginViewSet, basename="auth_login")
router.register("auth/logout", LogoutViewSet, basename="auth_logout")

# Self data API
# This should only allow access to data belonging to the current user
router.register("self/info", UserDataViewSet, basename="self_user")


urlpatterns = []
if settings.DEBUG:
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

    urlpatterns += [
        path("openapi/", SpectacularAPIView.as_view(), name="openapi"),
        path("openapi/swagger-ui/", SpectacularSwaggerView.as_view(url_name="api-v2:openapi"), name="swagger-ui"),
        path("openapi/redoc/", SpectacularRedocView.as_view(url_name="api-v2:openapi"), name="redoc"),
    ]

urlpatterns += [
    path("", include(router.urls)),
]

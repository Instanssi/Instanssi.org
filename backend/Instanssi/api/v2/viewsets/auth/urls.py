from django.urls import URLPattern, URLResolver
from rest_framework import routers

from Instanssi.api.v2.viewsets.auth.login import LoginViewSet
from Instanssi.api.v2.viewsets.auth.logout import LogoutViewSet
from Instanssi.api.v2.viewsets.auth.social_auth import SocialAuthUrlsViewSet

router = routers.SimpleRouter()
router.register("social_urls", SocialAuthUrlsViewSet, basename="auth_social_urls")
router.register("login", LoginViewSet, basename="auth_login")
router.register("logout", LogoutViewSet, basename="auth_logout")

urlpatterns: list[URLPattern | URLResolver] = router.urls

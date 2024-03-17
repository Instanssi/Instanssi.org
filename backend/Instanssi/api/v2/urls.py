from django.urls import include, path
from rest_framework import routers

app_name = "api-v2"


class InstanssiV2APIRoot(routers.APIRootView):
    """
    Instanssi v2 API.
    """

    pass


class V2CustomRouter(routers.DefaultRouter):
    APIRootView = InstanssiV2APIRoot


router = V2CustomRouter()


urlpatterns = [
    path("", include(router.urls)),
]

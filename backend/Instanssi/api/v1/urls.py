from django.conf.urls import include
from django.urls import path
from rest_framework import routers

from .viewsets.store import StoreItemViewSet, StoreTransactionViewSet

app_name = "api"

router = routers.SimpleRouter()
router.register(r"store_items", StoreItemViewSet, basename="store_items")
router.register(r"store_transaction", StoreTransactionViewSet, basename="store_transaction")

urlpatterns = [
    path("", include(router.urls)),
]

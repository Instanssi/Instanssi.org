from django.urls import URLPattern, URLResolver, include, path
from rest_framework import routers

from Instanssi.api.v2.viewsets.infodesk import (
    InfodeskTransactionItemViewSet,
    InfodeskTransactionViewSet,
)

infodesk_router = routers.SimpleRouter()
infodesk_router.register("transactions", InfodeskTransactionViewSet, basename="infodesk_transactions")
infodesk_router.register(
    "transaction_items", InfodeskTransactionItemViewSet, basename="infodesk_transaction_items"
)

urlpatterns: list[URLPattern | URLResolver] = [
    path("event/<int:event_pk>/", include(infodesk_router.urls)),
]

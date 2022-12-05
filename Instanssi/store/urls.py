from django.conf.urls import include
from django.urls import path
from django.views.generic import TemplateView

from Instanssi.store.views import ta_view, ti_view

app_name = "store"


urlpatterns = [
    path("", TemplateView.as_view(template_name="store/index.html"), name="index"),
    path("order/", TemplateView.as_view(template_name="store/store.html"), name="order"),
    path("terms/", TemplateView.as_view(template_name="store/terms.html"), name="terms"),
    path("privacy/", TemplateView.as_view(template_name="store/privacy.html"), name="privacy"),
    path("pm/", include("Instanssi.store.methods.urls", namespace="pm")),
    path("ti/<slug:item_key>/", ti_view, name="ti_view"),
    path("ta/<slug:transaction_key>/", ta_view, name="ta_view"),
]

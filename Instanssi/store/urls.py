from django.conf.urls import include, url
from django.views.generic import TemplateView

from Instanssi.store.views import ta_view, ti_view

app_name = "store"


urlpatterns = [
    url(r"^$", TemplateView.as_view(template_name="store/index.html"), name="index"),
    url(r"^order/$", TemplateView.as_view(template_name="store/store.html"), name="order"),
    url(r"^terms/$", TemplateView.as_view(template_name="store/terms.html"), name="terms"),
    url(r"^privacy/$", TemplateView.as_view(template_name="store/privacy.html"), name="privacy"),
    url(r"^pm/", include("Instanssi.store.methods.urls", namespace="pm")),
    url(r"^ti/(?P<item_key>\w+)/$", ti_view, name="ti_view"),
    url(r"^ta/(?P<transaction_key>\w+)/$", ta_view, name="ta_view"),
]

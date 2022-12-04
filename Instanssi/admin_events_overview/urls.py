from django.conf.urls import url

from Instanssi.admin_events_overview.views import index

app_name = "admin_events_overview"


urlpatterns = [
    url(r"^$", index, name="index"),
]

from django.urls import path

from Instanssi.admin_events_overview.views import index

app_name = "admin_events_overview"


urlpatterns = [
    path("", index, name="index"),
]

from django.urls import path

from Instanssi.admin_events.views import delete, edit, index

app_name = "admin_events"


urlpatterns = [
    path("", index, name="index"),
    path("edit/<int:event_id>/", edit, name="edit"),
    path("delete/<int:event_id>/", delete, name="delete"),
]

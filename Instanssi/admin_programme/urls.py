from django.urls import path

from Instanssi.admin_programme.views import delete, edit, index

app_name = "admin_programme"


urlpatterns = [
    path("", index, name="index"),
    path("delete/<int:event_id>/", delete, name="delete"),
    path("edit/<int:event_id>/", edit, name="edit"),
]

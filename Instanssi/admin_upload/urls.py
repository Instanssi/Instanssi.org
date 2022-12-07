from django.urls import path

from Instanssi.admin_upload.views import delete_file, edit_file, index

app_name = "admin_upload"


urlpatterns = [
    path("", index, name="index"),
    path("delete/<int:file_id>/", delete_file, name="delete"),
    path("edit/<int:file_id>/", edit_file, name="edit"),
]

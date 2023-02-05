from django.urls import path

from Instanssi.admin_blog.views import delete, edit, index

app_name = "admin_blog"


urlpatterns = [
    path("", index, name="index"),
    path("delete/<int:entry_id>/", delete, name="delete"),
    path("edit/<int:entry_id>/", edit, name="edit"),
]

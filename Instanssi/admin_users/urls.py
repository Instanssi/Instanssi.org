from django.urls import path

from Instanssi.admin_users.views import (
    apps,
    delete,
    delete_app,
    edit,
    index,
    log,
    users,
)

app_name = "admin_users"


urlpatterns = [
    path("", index, name="index"),
    path("users/<int:su_id>/delete/", delete, name="delete"),
    path("users/<int:su_id>/edit/", edit, name="edit"),
    path("users/", users, name="users"),
    path("apps/<int:app_id>/delete/", delete_app, name="delete_app"),
    path("apps/", apps, name="apps"),
]

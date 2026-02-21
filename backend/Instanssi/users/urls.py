from django.urls import path

from Instanssi.users.views import profile_view

app_name = "users"

urlpatterns = [
    path("profile/", profile_view, name="profile"),
]

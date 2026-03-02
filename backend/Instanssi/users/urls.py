from django.urls import path

from Instanssi.users.views import loggedout, profile

app_name = "users"


urlpatterns = [
    path("profile/", profile, name="profile"),
    path("loggedout/", loggedout, name="loggedout"),
]

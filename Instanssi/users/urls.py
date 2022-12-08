from django.urls import path

from Instanssi.users.views import loggedout, login, logout, profile

app_name = "users"


urlpatterns = [
    path("profile/", profile, name="profile"),
    path("login/", login, name="login"),
    path("logout/", logout, name="logout"),
    path("loggedout/", loggedout, name="loggedout"),
]

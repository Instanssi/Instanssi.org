from django.conf.urls import url

from Instanssi.users.views import loggedout, login, logout, profile

app_name = "users"


urlpatterns = [
    url(r"^profile/$", profile, name="profile"),
    url(r"^login/$", login, name="login"),
    url(r"^logout/$", logout, name="logout"),
    url(r"^loggedout/$", loggedout, name="loggedout"),
]

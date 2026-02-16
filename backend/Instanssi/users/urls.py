from django.urls import path
from django.views.generic import RedirectView

from Instanssi.users.views import profile

app_name = "users"


urlpatterns = [
    path("profile/", profile, name="profile"),
    path("login/", RedirectView.as_view(pattern_name="account_login"), name="login"),
    path("logout/", RedirectView.as_view(pattern_name="account_logout"), name="logout"),
]

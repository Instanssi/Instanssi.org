from django.urls import path

from Instanssi.admin_profile.views import password, profile

app_name = "admin_profile"


urlpatterns = [
    path("", profile, name="index"),
    path("password/", password, name="password"),
]

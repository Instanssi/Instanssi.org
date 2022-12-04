from django.conf.urls import url

from Instanssi.admin_profile.views import password, profile

app_name = "admin_profile"


urlpatterns = [
    url(r"^$", profile, name="index"),
    url(r"^password/", password, name="password"),
]

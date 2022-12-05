from django.urls import path

from Instanssi.admin_base.views import index

app_name = "admin_base"


urlpatterns = [
    path("", index, name="index"),
]

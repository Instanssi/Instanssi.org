from django.urls import path

from Instanssi.management.views import dummy_index

app_name = "management"

urlpatterns = [
    path("", dummy_index, name="index"),
]

from django.urls import path

from Instanssi.admin_utils.views import db_checker, diskcleaner, index

app_name = "admin_utils"


urlpatterns = [
    path("", index, name="index"),
    path("diskcleaner/", diskcleaner, name="diskcleaner"),
    path("dbchecker/", db_checker, name="dbchecker"),
]

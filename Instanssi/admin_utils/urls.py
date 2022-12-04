from django.conf.urls import url
from Instanssi.admin_utils.views import index, diskcleaner, dbchecker

app_name = "admin_utils"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^diskcleaner/', diskcleaner, name="diskcleaner"),
    url(r'^dbchecker/', dbchecker, name="dbchecker"),
]

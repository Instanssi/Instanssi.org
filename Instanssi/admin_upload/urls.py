from django.conf.urls import url
from Instanssi.admin_upload.views import index, deletefile, editfile

app_name = "admin_upload"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^delete/(?P<file_id>\d+)/', deletefile, name="delete"),
    url(r'^edit/(?P<file_id>\d+)/', editfile, name="edit"),
]

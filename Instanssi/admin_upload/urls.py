# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_upload.views import index, deletefile, editfile

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^delete/(?P<file_id>\d+)/', deletefile, name="delete"),
    url(r'^edit/(?P<file_id>\d+)/', editfile, name="edit"),
]

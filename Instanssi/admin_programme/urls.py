# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_programme.views import index, delete, edit

app_name = "admin_programme"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^delete/(?P<pev_id>\d+)/', delete, name="delete"),
    url(r'^edit/(?P<pev_id>\d+)/', edit, name="edit"),
]

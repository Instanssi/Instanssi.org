# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_utils.views import index, diskcleaner, dbchecker


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^diskcleaner/', diskcleaner, name="diskcleaner"),
    url(r'^dbchecker/', dbchecker, name="dbchecker"),
]

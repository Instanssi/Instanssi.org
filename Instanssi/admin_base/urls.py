# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_base.views import index

app_name = "admin_base"


urlpatterns = [
    url(r'^$', index, name="index"),
]

# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_base.views import index

urlpatterns = [
    url(r'^$', index, name="index"),
]

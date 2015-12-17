# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_events_overview.views import index

urlpatterns = [
    url(r'^$', index, name="index"),
]

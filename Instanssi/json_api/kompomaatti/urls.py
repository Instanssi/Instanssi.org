# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.json_api.kompomaatti.views import competitions_get, compos_get, events_get

urlpatterns = [
    url(r'^competitions/$', competitions_get, name="competitions_get"),
    url(r'^compos/$', compos_get, name="compos_get"),
    url(r'^events/', events_get, name="events_get"),
]

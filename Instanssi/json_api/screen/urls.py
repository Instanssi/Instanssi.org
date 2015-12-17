# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.json_api.screen.views import song_get, song_set


urlpatterns = [
    url(r'^np/$', song_get, name="song_get"),
    url(r'^np/set/$', song_set, name="song_set"),
]

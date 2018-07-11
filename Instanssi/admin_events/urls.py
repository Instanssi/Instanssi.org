# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_events.views import index, edit, delete

app_name = "admin_events"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^edit/(?P<event_id>\d+)/', edit, name="edit"),
    url(r'^delete/(?P<event_id>\d+)/', delete, name="delete"),
]

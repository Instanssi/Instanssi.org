# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_events.views',
    url(r'^$', 'index', name="index"),
    url(r'^edit/(?P<event_id>\d+)/', 'edit', name="edit"),
    url(r'^delete/(?P<event_id>\d+)/', 'delete', name="delete"),
)
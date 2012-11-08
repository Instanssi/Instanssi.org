# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_events.views',
    url(r'^$', 'index', name="events"),
    url(r'^edit/(?P<event_id>\d+)/', 'edit', name="events-edit"),
    url(r'^delete/(?P<event_id>\d+)/', 'delete', name="events-delete"),
)
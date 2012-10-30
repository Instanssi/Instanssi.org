# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_events.views',
    url(r'^$', 'index'),
    url(r'^edit/(?P<event_id>\d+)/', 'edit'),
    url(r'^delete/(?P<event_id>\d+)/', 'delete'),
)
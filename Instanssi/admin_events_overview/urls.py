# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_events_overview.views',
    url(r'^$', 'index', name="index"),
)

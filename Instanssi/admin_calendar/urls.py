# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_calendar.views',
    url(r'^$', 'index', name="index"),
    url(r'^delete/(?P<cev_id>\d+)/', 'delete', name="delete"),
    url(r'^edit/(?P<cev_id>\d+)/', 'edit', name="edit"),
)

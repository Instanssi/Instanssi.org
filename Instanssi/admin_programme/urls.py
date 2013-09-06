# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_programme.views',
    url(r'^$', 'index', name="index"),
    url(r'^delete/(?P<pev_id>\d+)/', 'delete', name="delete"),
    url(r'^edit/(?P<pev_id>\d+)/', 'edit', name="edit"),
)
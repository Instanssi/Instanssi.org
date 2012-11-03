# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_programme.views',
    url(r'^$', 'index', name="admin-programme"),
    url(r'^delete/(?P<pev_id>\d+)/', 'delete', name="admin-programme-delete"),
    url(r'^edit/(?P<pev_id>\d+)/', 'edit', name="admin-programme-edit"),
)
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_programme.views',
    url(r'^$', 'index', name="programme"),
    url(r'^delete/(?P<pev_id>\d+)/', 'delete', name="programme-delete"),
    url(r'^edit/(?P<pev_id>\d+)/', 'edit', name="programme-edit"),
)
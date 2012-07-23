# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_events.views',
    url(r'^$', 'index'),
    url(r'^settings/', 'settings'),
    url(r'~edit/', 'edit')
    url(r'^json/delete/', 'json_delete'),
)
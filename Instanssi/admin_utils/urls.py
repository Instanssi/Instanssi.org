# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_utils.views',
    url(r'^$', 'log', name="utils-index"),
    url(r'^log/', 'log', name="log"),
    url(r'^diskcleaner/', 'diskcleaner', name="diskcleaner"),
)
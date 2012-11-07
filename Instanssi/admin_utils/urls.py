# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_utils.views',
    url(r'^$', 'index', name="utils-index"),
    url(r'^diskcleaner/', 'diskcleaner', name="diskcleaner"),
    url(r'^dbchecker/', 'dbchecker', name="dbchecker"),
)
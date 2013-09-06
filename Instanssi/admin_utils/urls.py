# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_utils.views',
    url(r'^$', 'index', name="index"),
    url(r'^diskcleaner/', 'diskcleaner', name="diskcleaner"),
    url(r'^dbchecker/', 'dbchecker', name="dbchecker"),
)
# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_timingtool.views',
    url(r'^$', 'index', name="index"),
)
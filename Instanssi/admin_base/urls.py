# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_base.views',
    url(r'^$', 'index', name="index"),
)
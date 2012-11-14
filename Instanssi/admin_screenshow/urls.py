# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_screenshow.views',
    url(r'^$', 'index', name="index"),
)

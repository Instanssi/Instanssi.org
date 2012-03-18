# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'admin_base.views',
    url(r'^$', 'index'),
)
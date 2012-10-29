# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_base.views',
    url(r'^$', 'index'),
    url(r'^editor/', 'editor'),
)
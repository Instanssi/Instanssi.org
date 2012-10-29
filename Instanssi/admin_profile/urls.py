# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_profile.views',
    url(r'^$', 'index'),
    url(r'^password/', 'password'),
    url(r'^profile/', 'profile'),
)
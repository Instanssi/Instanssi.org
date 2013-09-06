# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_profile.views',
    url(r'^$', 'profile', name="index"),
    url(r'^password/', 'password', name="password"),
)
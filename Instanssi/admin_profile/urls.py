# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_profile.views',
    url(r'^$', 'profile'),
    url(r'^password/', 'password', name="admin-password"),
    url(r'^profile/', 'profile', name="admin-profile"),
)
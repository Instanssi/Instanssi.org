# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.users.views',
    url(r'^profile/$', 'profile', name="profile"),
    url(r'^login/$', 'login', name="login"),
    url(r'^logout/$', 'logout', name="logout"),
    url(r'^loggedout/$', 'loggedout', name="loggedout"),
)

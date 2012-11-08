# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_auth.views',
    url(r'^login/', 'login_action', name="login"),
    url(r'^logout/', 'logout_action', name="logout"),
    url(r'^loggedout/', 'logout_page', name="logout-page"),
)
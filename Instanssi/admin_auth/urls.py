# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_auth.views',
    url(r'^login/', 'login_action'),
    url(r'^logout/', 'logout_action'),
    url(r'^loggedout/', 'logout_page'),
)
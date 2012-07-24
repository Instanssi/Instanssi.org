# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_users.views',
    url(r'^$', 'index'),
    url(r'^openid/', 'openid'),
)
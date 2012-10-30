# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_users.views',
    url(r'^$', 'index'),
    url(r'^superusers', 'superusers'),
    url(r'^openid/', 'openid'),
)
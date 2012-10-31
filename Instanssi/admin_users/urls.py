# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_users.views',
    url(r'^$', 'superusers'),
    url(r'^superusers', 'superusers'),
    url(r'^deletesu/(?P<su_id>\d+)/', 'deletesu'),
    url(r'^editsu/(?P<su_id>\d+)/', 'editsu'),
    url(r'^openid/', 'openid'),
)
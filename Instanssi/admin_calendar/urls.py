# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_calendar.views',
    url(r'^$', 'index'),
    url(r'^add/', 'add'),
    url(r'^delete/(?P<cev_id>\d+)/', 'delete'),
    url(r'^edit/(?P<cev_id>\d+)/', 'edit'),
)

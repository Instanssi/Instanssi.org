# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

urlpatterns = patterns(
    'Instanssi.store.views',
    url(r'^notify/', 'notify_handler', name="notify"),
    url(r'^terms/', direct_to_template, {'template': 'store/terms.html'}, name='terms'),
    url(r'^privacy/', direct_to_template, {'template': 'store/privacy.html'}, name='privacy')
)

# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from Instanssi.store.views import StoreWizard

urlpatterns = patterns(
    'Instanssi.store.views',
    url(r'^$', 'index', name="index"),
    url(r'^order/$', StoreWizard.as_view(), name="order"),
    url(r'^notify/$', 'notify_handler', name="notify"),
    url(r'^terms/$', 'terms', name='terms'),
    url(r'^privacy/$', 'privacy', name='privacy'),
    url(r'^ti/(?P<item_key>\w+)/', 'ti_view', name='ti_view'),
    url(r'^ta/(?P<transaction_key>\w+)/', 'ta_view', name='ta_view')
)

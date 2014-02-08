# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns(
    'Instanssi.store.views',
    url(r'^notify/', 'notify_handler', name="notify"),
    url(r'^$', 'index', name="index"),
    url(r'^terms/', RedirectView.as_view(url='store/terms.html')),
    url(r'^privacy/', RedirectView.as_view(url='store/privacy.html')),
    url(r'^ti/(?P<item_key>\w+)/', 'ti_view', name='ti_view'),
    url(r'^ta/(?P<transaction_key>\w+)/', 'ta_view', name='ta_view')
)

# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url, include
from Instanssi.store.views import StoreWizard, store_forms

store_view = StoreWizard.as_view(
    store_forms, url_name='store:order_step', done_step_name='store:order_done')

urlpatterns = patterns(
    'Instanssi.store.views',
    url(r'^$', 'index', name="index"),
    url(r'^order/$', store_view, name='order'),
    url(r'^order/(?P<step>.+)/$', store_view, name='order_step'),
    url(r'^pm/', include('Instanssi.store.methods.urls', namespace='pm')),
    url(r'^terms/$', 'terms', name='terms'),
    url(r'^privacy/$', 'privacy', name='privacy'),
    url(r'^ti/(?P<item_key>\w+)/$', 'ti_view', name='ti_view'),
    url(r'^ta/(?P<transaction_key>\w+)/$', 'ta_view', name='ta_view')
)

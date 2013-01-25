# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.store.views',
	url(r'^success/', 'success_page', name="success"),
    url(r'^error/', 'error_page', name="error"),
    url(r'^notify/', 'notify_handler', name="notify"),
    url(r'^transaction/', 'transaction_handler', name="transaction")
)

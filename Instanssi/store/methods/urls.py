# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

urlpatterns = patterns(
    'Instanssi.store.methods',
    url(r'^paytrail/notify/$', 'paytrail.handle_notify', name="paytrail-notify"),
    url(r'^paytrail/failure/$', 'paytrail.handle_failure', name="paytrail-failure"),
    url(r'^paytrail/success/$', 'paytrail.handle_success', name="paytrail-success"),
)

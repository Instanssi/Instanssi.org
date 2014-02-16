# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from Instanssi.store.views import StoreWizard

urlpatterns = patterns(
    'Instanssi.store.methods',
    url(r'^paytrail/notify/$', 'paytrail.handle_notify', name="paytrail-notify"),
    url(r'^paytrail/failure/$', 'paytrail.handle_failure', name="paytrail-cancel"),
    url(r'^paytrail/success/$', 'paytrail.handle_success', name="paytrail-success"),

)

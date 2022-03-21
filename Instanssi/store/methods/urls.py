# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.store.methods import paytrail, no_method

app_name = "store"


urlpatterns = [
    url(r'^nomethod/success/$', no_method.handle_success, name="no-method-success"),
    url(r'^paytrail/notify/$', paytrail.handle_notify, name="paytrail-notify"),
    url(r'^paytrail/failure/$', paytrail.handle_failure, name="paytrail-failure"),
    url(r'^paytrail/success/$', paytrail.handle_success, name="paytrail-success"),
]

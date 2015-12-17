# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.store.methods import paytrail, bitpay

urlpatterns = [
    url(r'^paytrail/notify/$', paytrail.handle_notify, name="paytrail-notify"),
    url(r'^paytrail/failure/$', paytrail.handle_failure, name="paytrail-failure"),
    url(r'^paytrail/success/$', paytrail.handle_success, name="paytrail-success"),
    url(r'^bitpay/notify/$', bitpay.handle_notify, name="bitpay-notify"),
    url(r'^bitpay/failure/$', bitpay.handle_failure, name="bitpay-failure"),
    url(r'^bitpay/success/$', bitpay.handle_success, name="bitpay-success"),
]

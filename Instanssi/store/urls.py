# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url
from django.views.generic import RedirectView

urlpatterns = patterns(
    'Instanssi.store.views',
    url(r'^notify/', 'notify_handler', name="notify"),
    url(r'^terms/', RedirectView.as_view(url='store/terms.html')),
    url(r'^privacy/', RedirectView.as_view(url='store/privacy.html'))
)

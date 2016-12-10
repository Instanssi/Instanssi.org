# -*- coding: utf-8 -*-

from django.conf.urls import url, include
from django.views.generic import TemplateView

from Instanssi.store.views import index, terms, privacy, ti_view, ta_view

urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^order/$', TemplateView.as_view(template_name='store/store.html'), name='order'),
    url(r'^pm/', include('Instanssi.store.methods.urls', namespace='pm')),
    url(r'^terms/$', terms, name='terms'),
    url(r'^privacy/$', privacy, name='privacy'),
    url(r'^ti/(?P<item_key>\w+)/$', ti_view, name='ti_view'),
    url(r'^ta/(?P<transaction_key>\w+)/$', ta_view, name='ta_view')
]

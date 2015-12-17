# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_slides.views import index, slide_entries, slide_results


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^slide_entries/(?P<compo_id>\d+)/', slide_entries, name="entries"),
    url(r'^slide_results/(?P<compo_id>\d+)/', slide_results, name="results"),
]

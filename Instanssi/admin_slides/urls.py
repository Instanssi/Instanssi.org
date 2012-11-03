# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_slides.views',
    url(r'^$', 'index', name="admin-slides"),
    url(r'^slide_entries/(?P<compo_id>\d+)/', 'slide_entries', name="admin-slides-entries"),
    url(r'^slide_results/(?P<compo_id>\d+)/', 'slide_results', name="admin-slides-results"),
)
# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.kompomaatti_auth.views',
    url(r'^login/', 'login', name="kompomaatti-auth-login"),
)

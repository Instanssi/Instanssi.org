# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_profile.views import profile, password

app_name = "admin_profile"


urlpatterns = [
    url(r'^$', profile, name="index"),
    url(r'^password/', password, name="password"),
]

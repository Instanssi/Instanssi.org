# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from Instanssi import settings

# Use admin panel
admin.autodiscover()

# URLS
urlpatterns = patterns('',
    url(r'^2012/', include('main2012.urls')),
    url(r'^kompomaatti/', include('kompomaatti.urls')),
    url(r'^arkisto/', include('arkisto.urls')),
    url(r'^arkistoija/', include('arkistoija.urls')),
    url(r'^$', include('main2012.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^openid/', include('django_openid_auth.urls')),
)

# Serve media files through static.serve when running in debug mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
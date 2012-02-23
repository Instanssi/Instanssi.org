# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from Instanssi import settings

# Use admin panel
admin.autodiscover()

# URLS
urlpatterns = patterns('',
    url(r'^2012/', include('main2012.urls')),
    url(r'^arkisto/', include('arkisto.urls')),
    url(r'^$', include('main2012.urls')),
    url(r'^admin/', include(admin.site.urls)),
    (r'^openid/', include('django_openid_auth.urls')),
)

# Add Kompomaatti urls only if ACTIVE_EVENT_ID is not -1
if settings.ACTIVE_EVENT_ID != -1:
    urlpatterns += patterns('',
        url(r'^kompomaatti/', include('kompomaatti.urls')),
    )

# Serve media files through static.serve when running in debug mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
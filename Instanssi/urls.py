# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from Instanssi import settings

# Use admin panel
admin.autodiscover()

# URLS
urlpatterns = patterns('',
    url(r'^2012/', include('Instanssi.main2012.urls')),
    url(r'^control/', include('Instanssi.admin_base.urls')),
    url(r'^control/files/', include('Instanssi.admin_upload.urls')),
    url(r'^control/auth/', include('Instanssi.admin_auth.urls')),
    url(r'^control/blog/', include('Instanssi.admin_blog.urls')),
    url(r'^control/calendar/', include('Instanssi.admin_calendar.urls')),
    url(r'^control/arkisto/', include('Instanssi.admin_arkisto.urls')),
    url(r'^control/slides/', include('Instanssi.admin_slides.urls')),
    url(r'^control/events/', include('Instanssi.admin_events.urls')),
    url(r'^control/kompomaatti/', include('Instanssi.admin_kompomaatti.urls')),
    url(r'^control/users/', include('Instanssi.admin_users.urls')),
    url(r'^arkisto/', include('Instanssi.arkisto.urls')),
    url(r'^kompomaatti/', include('Instanssi.kompomaatti.urls')),
    url(r'^$', include('Instanssi.main2012.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openid/', include('django_openid_auth.urls')),
)

# Serve media files through static.serve when running in debug mode
if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
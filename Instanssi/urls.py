# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings

# Use admin panel
admin.autodiscover()

# URLS
urlpatterns = patterns('',
    url(r'^2012/', include('Instanssi.main2012.urls')),
    url(r'^manage/', include('Instanssi.admin_base.urls')),
    url(r'^manage/auth/', include('Instanssi.admin_auth.urls')),
    url(r'^manage/events/', include('Instanssi.admin_events.urls')),
    url(r'^manage/users/', include('Instanssi.admin_users.urls')),
    url(r'^manage/profile/', include('Instanssi.admin_profile.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/', include('Instanssi.admin_events_overview.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/files/', include('Instanssi.admin_upload.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/blog/', include('Instanssi.admin_blog.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/calendar/', include('Instanssi.admin_calendar.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/arkisto/', include('Instanssi.admin_arkisto.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/slides/', include('Instanssi.admin_slides.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/kompomaatti/', include('Instanssi.admin_kompomaatti.urls')),
    url(r'^manage/(?P<sel_event_id>\d+)/programme/', include('Instanssi.admin_programme.urls')),
    url(r'^blog/', include('Instanssi.ext_blog.urls')),
    url(r'^arkisto/', include('Instanssi.arkisto.urls')),
    url(r'^kompomaatti/', include('Instanssi.kompomaatti.urls')),
    url(r'^$', include('Instanssi.main2012.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^openid/', include('django_openid_auth.urls')),
)

# Serve media files through static.serve when running in debug mode
if getattr(settings, 'DEBUG'):
    urlpatterns += patterns('',
        (r'^uploads/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
    )
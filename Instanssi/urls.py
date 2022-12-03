# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django.conf import settings
from django.urls import reverse_lazy, path
from django.contrib import admin
from django.views.static import serve
from django.views.generic import RedirectView

# URLS
urlpatterns = [
    url('', include('social_django.urls', namespace='social')),
    url(r'^api/v1/', include('Instanssi.api.urls', namespace="api")),
    url(r'^2022/', include('Instanssi.main2022.urls', namespace="main2022")),
    url(r'^manage/events/', include('Instanssi.admin_events.urls', namespace='manage-events')),
    url(r'^manage/users/', include('Instanssi.admin_users.urls', namespace='manage-users')),
    url(r'^manage/profile/', include('Instanssi.admin_profile.urls', namespace='manage-profile')),
    url(r'^manage/utils/', include('Instanssi.admin_utils.urls', namespace='manage-utils')),
    url(r'^manage/store/', include('Instanssi.admin_store.urls', namespace='manage-store')),
    url(r'^manage/(?P<sel_event_id>\d+)/', include('Instanssi.admin_events_overview.urls', namespace='manage-overview')),
    url(r'^manage/(?P<sel_event_id>\d+)/files/', include('Instanssi.admin_upload.urls', namespace='manage-uploads')),
    url(r'^manage/(?P<sel_event_id>\d+)/blog/', include('Instanssi.admin_blog.urls', namespace='manage-blog')),
    url(r'^manage/(?P<sel_event_id>\d+)/arkisto/', include('Instanssi.admin_arkisto.urls', namespace='manage-arkisto')),
    url(r'^manage/(?P<sel_event_id>\d+)/slides/', include('Instanssi.admin_slides.urls', namespace='manage-slides')),
    url(r'^manage/(?P<sel_event_id>\d+)/screenshow/', include('Instanssi.admin_screenshow.urls', namespace='manage-screenshow')),
    url(r'^manage/(?P<sel_event_id>\d+)/kompomaatti/', include('Instanssi.admin_kompomaatti.urls', namespace='manage-kompomaatti')),
    url(r'^manage/(?P<sel_event_id>\d+)/programme/', include('Instanssi.admin_programme.urls', namespace='manage-programme')),
    url(r'^manage/', include('Instanssi.admin_base.urls', namespace='manage-base')),
    url(r'^users/', include('Instanssi.users.urls', namespace='users')),
    url(r'^blog/', include('Instanssi.ext_blog.urls', namespace="ext-blog")),
    url(r'^arkisto/', include('Instanssi.arkisto.urls', namespace='archive')),
    url(r'^kompomaatti/', include('Instanssi.kompomaatti.urls', namespace="km")),
    url(r'^screen/', include('Instanssi.screenshow.urls', namespace="screen")),
    url(r'^store/', include('Instanssi.store.urls', namespace='store')),
    url(r'^infodesk/', include('Instanssi.infodesk.urls', namespace='infodesk')),
    url(r'^$', RedirectView.as_view(url=reverse_lazy('main2022:index')), name='root-index')
]

# Add admin panel link if debug mode is on
if settings.DEBUG or settings.ADMIN:
    admin.autodiscover()
    urlpatterns += [
        path('admin/', admin.site.urls),
    ]

if settings.DEBUG:
    # Serve media files through static.serve when running in debug mode
    # Also, show debug_toolbar if debugging is on
    urlpatterns += [
        url(r'^uploads/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]


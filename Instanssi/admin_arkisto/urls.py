# -*- coding: utf-8 -*-

from django.conf.urls.defaults import patterns, url

urlpatterns = patterns(
    'Instanssi.admin_arkisto.views',
    url(r'^$', 'index', name="admin-archive"),
    url(r'^archiver/', 'archiver', name="admin-archiver"),
    url(r'^show/', 'show', name="admin-archiver-show"),
    url(r'^hide/', 'hide', name="admin-archiver-hide"),
    url(r'^transferrights/', 'transferrights', name="admin-archiver-tr"),
    url(r'^optimizescores/', 'optimizescores', name="admin-archiver-os"),
    url(r'^removeoldvotes/', 'removeoldvotes', name="admin-archiver-rv"),
    url(r'^vids/', 'vids', name="admin-vids"),
    url(r'^vidcats/', 'cats', name="admin-vidcats"),
    url(r'^deletevid/(?P<video_id>\d+)/', 'deletevid', name="admin-vids-delete"),
    url(r'^deletecat/(?P<category_id>\d+)/', 'deletecat', name="admin-vidcats-delete"),
    url(r'^editvid/(?P<video_id>\d+)/', 'editvid', name="admin-vids-edit"),
    url(r'^editcat/(?P<category_id>\d+)/', 'editcat', name="admin-vidcats-edit"),
)

# -*- coding: utf-8 -*-

from django.conf.urls import url
from Instanssi.admin_arkisto.views import index, archiver, show, hide, transferrights, optimizescores, removeoldvotes, \
    vids, cats, deletecat, deletevid, editcat, editvid

app_name = "admin_arkisto"


urlpatterns = [
    url(r'^$', index, name="index"),
    url(r'^archiver/', archiver, name="archiver"),
    url(r'^show/', show, name="archiver-show"),
    url(r'^hide/', hide, name="archiver-hide"),
    url(r'^transferrights/', transferrights, name="archiver-tr"),
    url(r'^optimizescores/', optimizescores, name="archiver-os"),
    url(r'^removeoldvotes/', removeoldvotes, name="archiver-rv"),
    url(r'^vids/', vids, name="vids"),
    url(r'^vidcats/', cats, name="vidcats"),
    url(r'^deletevid/(?P<video_id>\d+)/', deletevid, name="vids-delete"),
    url(r'^deletecat/(?P<category_id>\d+)/', deletecat, name="vidcats-delete"),
    url(r'^editvid/(?P<video_id>\d+)/', editvid, name="vids-edit"),
    url(r'^editcat/(?P<category_id>\d+)/', editcat, name="vidcats-edit"),
]

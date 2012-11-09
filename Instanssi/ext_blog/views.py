# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import Event

class blog_feed(Feed):
    title = "Instanssi.org Blogi"
    link = "http://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def get_object(self, request, event_id):
        return get_object_or_404(Event, pk=event_id)

    def items(self, obj):
        entries = []
        for entry in BlogEntry.objects.filter(event=obj, public=True).order_by('date'):
            entry.event_url = obj.mainurl
            entries.append(entry)
        return entries

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text
    
    def item_link(self, item):
        print item.event_url
        if item.event_url and len(item.event_url) > 0:
            return item.event_url + '#blog'+str(item.id)
        return "http://instanssi.org/#blog"+str(item.id)
# -*- coding: utf-8 -*-

from django.contrib.syndication.views import Feed, FeedDoesNotExist
from django.shortcuts import get_object_or_404
from Instanssi.ext_blog.models import BlogEntry
from Instanssi.kompomaatti.models import Event

class BlogEntryFeed(Feed):
    title = "Instanssi.org Blog Feed"
    link = "http://instanssi.org"
    description = "Instanssi-demopartyn uusimmat uutiset."

    def get_object(self, request, event_id):
        self.host = request.get_host()
        return get_object_or_404(Event, pk=event_id)

    def items(self, obj):
        return BlogEntry.objects.filter(event=obj, public=True).order_by('-date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text
    
    def item_link(self, item):
        return "http://"+self.host+"/blogentry/"+str(item.id)+"/"
# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi import settings
from django.http import HttpResponse
import feedparser
from models import BlogEntry
from datetime import datetime, timedelta
import time

# A nice wrapper
def render_custom(tpl, ext={}):
    vars = {
        'googleapikey': settings.GOOGLEAPIKEY,
        'googleanalytics': settings.GOOGLEANALYTICS,
        'debugmode': settings.DEBUG
    }
    return render_to_response(tpl, dict(vars.items() + ext.items()))

# Pages
def index(request):
    entries = BlogEntry.objects.all().order_by('date').reverse()
    return render_custom("main2012/index.html", {'blogitems': entries})

def info(request):
    return render_custom("main2012/info.html")

def aikataulu(request):
    return render_custom('main2012/aikataulu.html')

def english(request):
    return render_custom('main2012/english.html')

def kompot(request):
    return render_custom('main2012/kompot.html')

def stream(request):
    return render_custom('main2012/stream.html')

def ohjelma(request):
    return render_custom('main2012/ohjelma.html')

def liput(request):
    return render_custom('main2012/liput.html')

def yhteystiedot(request):
    return render_custom('main2012/yhteystiedot.html')

def updateblog(request):
    # Get feed
    url = 'http://blog.instanssi.org/feeds/posts/default'
    feed = feedparser.parse(url)
    
    # Delete old entries
    BlogEntry.objects.filter(locked=False).delete()
    
    # Get items that have changed
    for item in feed['items']:
        locked = False
        try:
            oldentry = BlogEntry.objects.get(title=item['title'])
            locked = oldentry.locked
        except BlogEntry.DoesNotExist:
            pass
        
        if not locked:
            timestamp = datetime.fromtimestamp(time.mktime(item['published_parsed'])) + timedelta(hours=2)
            entry = BlogEntry()
            entry.title = item['title']
            entry.summary = item['summary']
            entry.date = timestamp
            entry.link = item['link']
            entry.name = item['authors'][0]['name']
            entry.save()
        
    # Just return "ok"
    return HttpResponse("ok");


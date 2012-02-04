# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi import settings
from django.http import HttpResponse
import feedparser
from models import BlogEntry
from datetime import datetime
import time

# A nice wrapper
def render_custom(tpl):
    return render_to_response(tpl, {
        'googleapikey': settings.GOOGLEAPIKEY,
        'googleanalytics': settings.GOOGLEANALYTICS,
        'debugmode': settings.DEBUG
    })

# Pages
def index(request):
    return render_custom("main2012/index.html")

def info(request):
    return render_custom("main2012/info.html")

def aikataulu(request):
    return render_custom('main2012/aikataulu.html')

def english(request):
    return render_custom('main2012/english.html')

def kompot(request):
    return render_custom('main2012/kompot.html')

def liput(request):
    return render_custom('main2012/liput.html')

def yhteystiedot(request):
    return render_custom('main2012/yhteystiedot.html')

def updateblog(request):
    # Get feed
    url = 'http://blog.instanssi.org/feeds/posts/default'
    feed = feedparser.parse(url)
    
    # Delete old entries
    BlogEntry.objects.all().delete()
    
    # Get items that have changed
    for item in feed['items']:
        timestamp = datetime.fromtimestamp(time.mktime(item['published_parsed']))
        entry = BlogEntry()
        entry.title = item['title']
        entry.summary = item['summary']
        entry.date = timestamp
        entry.link = item['link']
        entry.name = item['authors'][0]['name']
        entry.save()
        
    # Just return "ok"
    return HttpResponse("ok");


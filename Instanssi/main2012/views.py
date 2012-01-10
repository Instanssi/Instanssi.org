# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi import settings
from django.http import HttpResponse
import urllib2
from urllib2 import URLError

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

# evil h4x
def feed(request):
    req = urllib2.Request('http://blog.instanssi.org/feeds/posts/default')
    data = ''
    try:
        urllib2.urlopen(req)
        response = urllib2.urlopen(req, timeout=3)
        data = response.read()
    except URLError, e:
        pass
    return HttpResponse(data);

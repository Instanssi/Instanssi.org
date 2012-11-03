# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.conf import settings
from django.http import HttpResponse
from datetime import datetime, timedelta
import time

# A nice wrapper
def render_custom(tpl, ext={}):
    vars = {
        'googleapikey': getattr(settings, 'GOOGLEAPIKEY'),
        'googleanalytics': getattr(settings, 'GOOGLEANALYTICS'),
        'debugmode': getattr(settings, 'DEBUG'),
    }
    return render_to_response(tpl, dict(vars.items() + ext.items()))

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

def stream(request):
    return render_custom('main2012/stream.html')

def ohjelma(request):
    return render_custom('main2012/ohjelma.html')

def liput(request):
    return render_custom('main2012/liput.html')

def yhteystiedot(request):
    return render_custom('main2012/yhteystiedot.html')


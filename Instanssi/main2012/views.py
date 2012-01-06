# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from Instanssi import settings

# A nice wrapper
def render_custom(tpl):
    return render_to_response(tpl, {
        'googleapikey': settings.GOOGLEAPIKEY,
        'googleanalytics': settings.GOOGLEANALYTICS
    })

# Pages
def index(request):
    return render_custom("index.html")

def info(request):
    return render_custom("info.html")

def aikataulu(request):
    return render_custom('aikataulu.html')

def english(request):
    return render_custom('english.html')

def kompot(request):
    return render_custom('kompot.html')

def liput(request):
    return render_custom('liput.html')

def yhteystiedot(request):
    return render_custom('yhteystiedot.html')
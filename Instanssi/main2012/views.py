# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader
from django.shortcuts import render_to_response

# 
# At the moment, all the pages are loaded by using separate functions. 
# There aren't that many different pages, so it's acceptable :P
#

def index(request):
    t = loader.get_template('index.html')
    c = Context({
        'request': request,
    })
    return HttpResponse(t.render(c))

def info(request):
    googleapikey = "AIzaSyCy8WMM6bkEdsDUE2_jPax35M0PXP87W5s";
    return render_to_response('info.html', {'googleapikey': googleapikey})

def aikataulu(request):
    return render_to_response('aikataulu.html')

def english(request):
    return render_to_response('english.html')

def kompot(request):
    return render_to_response('kompot.html')

def liput(request):
    return render_to_response('liput.html')

def yhteystiedot(request):
    return render_to_response('yhteystiedot.html')
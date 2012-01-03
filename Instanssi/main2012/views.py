# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader

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
    t = loader.get_template('info.html')
    c = Context({
        'request': request,
    })
    return HttpResponse(t.render(c))
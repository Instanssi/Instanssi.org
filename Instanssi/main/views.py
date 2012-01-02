# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.template import Context, loader


def index(request):
    t = loader.get_template('index.html')
    c = Context({
        'request': request,
    })
    return HttpResponse(t.render(c))

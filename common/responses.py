# -*- coding: utf-8 -*-

from django.http import HttpResponse
from django.utils import simplejson

def JSONResponse(data):
    return HttpResponse(simplejson.dumps(data), mimetype='application/json')


# -*- coding: utf-8 -*-

from django.http import HttpResponse
import json

def JSONResponse(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


# -*- coding: utf-8 -*-

from django.http import HttpResponse
import json


def rest_api(view_func):
    def json_view(request, *args, **kwargs):
        request.json_data = {}
        if request.method == 'POST':
            try:
                request.json_data = json.loads(request.body)
            except ValueError:
                pass
        return view_func(request, *args, **kwargs)
    json_view.csrf_exempt = True
    return json_view


def RestResponse(data=None, code=200, error_text=''):
    out = {
        'code': code,
        'errortext': error_text,
        'content': data,
    }
    return HttpResponse(json.dumps(out), content_type='application/json')

import json

from django.http import HttpResponse


def JSONResponse(data):
    return HttpResponse(json.dumps(data), content_type="application/json")

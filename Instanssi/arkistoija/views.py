# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import HttpResponse
from Instanssi import settings
import Instanssi.kompomaatti.models as kmodels
import Instanssi.arkisto.models as amodels

def index(request):
    return render_to_response("arkistoija/index.html", {
    
    })

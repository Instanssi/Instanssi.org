# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response

def index(request):
    return render_to_response('kompomaatti/index.html')

def compo(request):
    return render_to_response('kompomaatti/compo.html')

def entry(request):
    return render_to_response('kompomaatti/entry.html')

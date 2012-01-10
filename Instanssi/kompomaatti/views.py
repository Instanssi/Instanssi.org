# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from models import Compo, Entry
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404  

def custom_render(tpl, context={}):
    compos = Compo.objects.all()
    context['compos'] = compos
    return render_to_response(tpl, context)


def index(request):
    return custom_render('kompomaatti/index.html')


def help(request):
    return custom_render('kompomaatti/help.html')


def compo(request, compo_id):
    try:
        compo = Compo.objects.get(id=compo_id)
    except ObjectDoesNotExist:
        raise Http404
    return custom_render('kompomaatti/compo.html', {'compo': compo})


def compolist(request):
    return custom_render('kompomaatti/compolist.html')


def entry(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    return custom_render('kompomaatti/entry.html', {'entry': entry})

# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from models import Compo, Entry
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from forms import AddEntryForm
from django.template import RequestContext

def custom_render(request, tpl, context={}):
    compos = Compo.objects.all()
    context['compos'] = compos
    return render_to_response(tpl, context, context_instance=RequestContext(request))


def index(request):
    return custom_render(request, 'kompomaatti/index.html')


def help(request):
    return custom_render(request, 'kompomaatti/help.html')


def myprods(request):
    if request.method == 'POST':
        addform = AddEntryForm(request.POST) 
        if addform.is_valid(): 
            pass
    else:
        addform = AddEntryForm() 
        
    return custom_render(request, 'kompomaatti/myprods.html', {
        'addform': addform,
    })


def compo(request, compo_id):
    try:
        compo = Compo.objects.get(id=compo_id)
    except ObjectDoesNotExist:
        raise Http404
    return custom_render(request, 'kompomaatti/compo.html', {'compo': compo})


def compolist(request):
    return custom_render(request, 'kompomaatti/compolist.html')


def entry(request, entry_id):
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    return custom_render(request, 'kompomaatti/entry.html', {'entry': entry})

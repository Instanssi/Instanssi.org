# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone

from Instanssi.main2014.models import ToimistoJahti, ToimistoSuoritus
from Instanssi.main2014.forms import ToimistoCodeForm
from Instanssi.common.auth import user_access_required


def pageloader(request, templatename):
    return render(request, 'main2014/'+templatename+'.html', {
        'event_id': 8, 
        'templatename': templatename,
    })


def jahti(request, hint_id):
    hint = get_object_or_404(ToimistoJahti, key=hint_id)
    
    return render(request, 'main2014/toimisto/jahti.html', {
        'event_id': 8,
        'hint': hint.help,
    })


@user_access_required
def reportointi(request):
    is_done = True
    try:
        ToimistoSuoritus.objects.get(user=request.user)
    except ToimistoSuoritus.DoesNotExist:
        is_done = False
    
    if request.method == 'POST' and is_done == False:
        codeform = ToimistoCodeForm(request.POST)
        if codeform.is_valid():
            s = ToimistoSuoritus()
            s.user = request.user
            s.nick = codeform.cleaned_data['nick']
            s.time = timezone.now()
            s.save()
            return HttpResponseRedirect(reverse('main2014:toimisto-kiitos'))
    else:
        codeform = ToimistoCodeForm()
    
    return render(request, 'main2014/toimisto/reportointi.html', {
        'event_id': 8,
        'form': codeform,
        'is_done': is_done,
    })


@user_access_required
def kiitos(request):
    par = get_object_or_404(ToimistoSuoritus, user=request.user)
    users = ToimistoSuoritus.objects.all().order_by('time')
    
    return render(request, 'main2014/toimisto/kiitos.html', {
        'event_id': 8,
        'participant': par,
        'users': users,
    })

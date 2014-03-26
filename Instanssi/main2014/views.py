# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from Instanssi.main2014.models import ToimistoJahti,ToimistoSuoritus
from Instanssi.main2014.forms import ToimistoCodeForm
from common.auth import user_access_required
from datetime import datetime

def pageloader(request, templatename):
    return render_to_response('main2014/'+templatename+'.html', {
        'event_id': 8, 
        'templatename': templatename,
    }, context_instance=RequestContext(request))
    
def jahti(request, hint_id):
    hint = get_object_or_404(ToimistoJahti, key=hint_id)
    
    return render_to_response('main2014/toimisto/jahti.html', {
        'event_id': 8,
        'hint': hint.help,
    }, context_instance=RequestContext(request))

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
            s.time = datetime.now()
            s.save()
            return HttpResponseRedirect(reverse('main2014:toimisto-kiitos'))
    else:
        codeform = ToimistoCodeForm()
    
    return render_to_response('main2014/toimisto/reportointi.html', {
        'event_id': 8,
        'form': codeform,
        'is_done': is_done,
    }, context_instance=RequestContext(request))

@user_access_required
def kiitos(request):
    par = get_object_or_404(ToimistoSuoritus, user=request.user)
    users = ToimistoSuoritus.objects.all().order_by('-time')
    
    return render_to_response('main2014/toimisto/kiitos.html', {
        'event_id': 8,
        'participant': par,
        'users': users,
    }, context_instance=RequestContext(request))

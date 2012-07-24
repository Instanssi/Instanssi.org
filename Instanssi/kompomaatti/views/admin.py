# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.db import IntegrityError
from django.contrib.auth.decorators import login_required
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import random
import hashlib
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Event
from Instanssi.kompomaatti.forms import AdminEntryForm,AdminCompoForm,CreateTokensForm
from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc import entrysort
from Instanssi.dbsettings.models import Setting

@login_required
def editcompo(request, compo_id):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404

    # Get the compo
    try:
        compo = Compo.objects.get(id=compo_id)
    except VoteCodeRequest.DoesNotExist:
        raise Http404
    
    # Check if we got filled form
    if request.method == 'POST':
        form = AdminCompoForm(request.POST, instance=compo)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/kompomaatti/admin/') 
    else:
        form = AdminCompoForm(instance=compo)

    # Render
    return custom_render(request, 'kompomaatti/admin/editcompo.html', {
        'form': form,
    })

@login_required
def results(request, compo_id):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404

    # Get the compo
    try:
        c = Compo.objects.get(id=compo_id)
    except Entry.DoesNotExist:
        raise Http404
    
    # Get the entries
    entries = entrysort.sort_by_score(Entry.objects.filter(compo=c))

    # Render
    return custom_render(request, 'kompomaatti/admin/results.html', {
        'entries': entries,
        'compo': c,
    })

@login_required
def editentry(request, entry_id):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404

    # Get the entry
    try:
        entry = Entry.objects.get(id=entry_id)
    except Entry.DoesNotExist:
        raise Http404

    # Check if we got filled form
    if request.method == 'POST':
        form = AdminEntryForm(request.POST, request.FILES, instance=entry)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/kompomaatti/admin/') 
    else:
        form = AdminEntryForm(instance=entry)

    # Render
    return custom_render(request, 'kompomaatti/admin/editentry.html', {
        'form': form,
    })

@login_required
def addcompo(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Get active event id
    active_event_id = Setting.get('active_event_id', 'events', -1)
    
    # Check if we got filled form
    if request.method == 'POST':
        form = AdminCompoForm(request.POST)
        if form.is_valid():
            # Get the Event. If this fails, everything should fail anyways. So, don't catch exception.
            event = Event.objects.get(id=active_event_id)
            
            # Save compo
            compo = form.save(commit=False)
            compo.event = event
            compo.save()
            return HttpResponseRedirect('/kompomaatti/admin/') 
    else:
        form = AdminCompoForm()

    # Render
    return custom_render(request, 'kompomaatti/admin/addcompo.html', {
        'form': form,
    })

@login_required
def printcodes(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Get free votecodes
    codes = VoteCode.objects.filter(associated_to=None)
    
    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(mimetype='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=votecodes.pdf'

    # Create the PDF object,
    p = canvas.Canvas(response)
    p.setAuthor(u"Kompomaatti")
    p.setTitle(u"Äänestyskoodeja")
    p.setFont("Helvetica-Oblique", 18)

    # Print codes
    height = 0
    step = 2.12*cm
    perpage = 14
    codeno = 0
    for code in codes:
        p.line(0,height,21*cm,height)
        p.drawString(1*cm, height+0.8*cm, u"Äänestyskoodi: "+code.key)
        height += step
        codeno += 1
        if codeno >= perpage:
            p.showPage()
            p.setFont("Helvetica-Oblique", 18)
            height = 0
            codeno = 0
    p.showPage()

    # Close the PDF object & dump out the response
    p.save()
    return response

@login_required
def admin(request):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
        
    # Check if we got filled form
    if request.method == 'POST':
        gentokensform = CreateTokensForm(request.POST)
        if gentokensform.is_valid():
            amount = int(gentokensform.cleaned_data['amount'])
            for n in range(amount):
                try:
                    c = VoteCode()
                    c.key = unicode(hashlib.md5(str(random.random())).hexdigest()[:8])
                    c.save()
                except IntegrityError:
                    n = n-1 # Ugly, may cause infinite loop...
            return HttpResponseRedirect('/kompomaatti/admin/') 
    else:
        gentokensform = CreateTokensForm()
        
    # Get active event id
    active_event_id = Setting.get('active_event_id', 'events', -1)
        
    # Get data
    compos = Compo.objects.filter(event=active_event_id)
    entries = Entry.objects.filter(compo__in=compos)
    tokens = VoteCode.objects.all()
    vcreqs = VoteCodeRequest.objects.all()
    event = Event.objects.get(id=active_event_id)
    
    # Just dump the page
    return custom_render(request, 'kompomaatti/admin/admin.html', {
        'tokens': tokens,
        'entries': entries,
        'rcompos': compos,
        'vcreqs': vcreqs,
        'event': event,
        'gentokensform': gentokensform,
    })

@login_required
def givecode(request, vcrid):
    # Make sure the user is superuser.
    if not request.user.is_superuser:
        raise Http404
    
    # Get the request
    try:
        vcr = VoteCodeRequest.objects.get(id=vcrid)
    except VoteCodeRequest.DoesNotExist:
        raise Http404
        
    # Add votecode for user. Bang your head to the wall until you succeed, etc.
    # Really, do something about this later!
    # TODO: Do something about this shit!
    done = False
    for i in range(25):
        try:
            c = VoteCode()
            c.key = unicode(hashlib.md5(str(random.random())).hexdigest()[:8])
            c.associated_to = vcr.user
            c.time = datetime.now()
            c.save()
            done = True
            break;
        except IntegrityError:
            pass
    
    if not done:
        return HttpResponse("Virhe yritettäessä lisätä satunnaista avainta ... FIXME!")
            
    # Delete request
    vcr.delete()
    
    # Return to admin page
    return HttpResponseRedirect('/kompomaatti/admin/') 

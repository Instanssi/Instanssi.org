# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
from Instanssi.dbsettings.models import Setting
from Instanssi.kompomaatti.models import Compo,Entry,VoteCodeRequest,VoteCode,Event,Competition,CompetitionParticipation
from Instanssi.admin_kompomaatti.forms import AdminCompoForm, AdminEntryForm, AdminEntryAddForm, CreateTokensForm, AdminCompetitionForm
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.misc import entrysort

# For votecode stuff
from django.db import IntegrityError
from datetime import datetime
import random
import hashlib
    
# For generating a paper version of votecodes
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
    
@login_required(login_url='/manage/auth/login/')
def competitions_browse(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get competitions
    competitions = Competition.objects.filter(event_id=int(sel_event_id))
    
    # Form handling
    if request.method == "POST":
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_competition'):
            raise Http403
        
        # Handle form
        competitionform = AdminCompetitionForm(request.POST)
        if competitionform.is_valid():
            data = competitionform.save(commit=False)
            data.event_id = int(sel_event_id)
            data.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/competitions/') 
    else:
        competitionform = AdminCompetitionForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competitions.html", {
        'competitions': competitions,
        'competitionform': competitionform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def competition_edit(request, sel_event_id, competition_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_competition'):
        raise Http403
    
    # Get competition
    competition = get_object_or_404(Competition, pk=competition_id)
    
    # Handle form
    if request.method == "POST":
        competitionform = AdminCompetitionForm(request.POST, instance=competition)
        if competitionform.is_valid():
            competitionform.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/competitions/') 
    else:
        competitionform = AdminCompetitionForm(instance=competition)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/competition_edit.html", {
        'competition': competition,
        'competitionform': competitionform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def competition_delete(request, sel_event_id, competition_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.delete_competition'):
        raise Http403
    
    # Delete competition
    try:
        Competition.objects.get(pk=competition_id).delete()
    except:
        pass
    
    # Redirect
    return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/competitions/') 
    
@login_required(login_url='/manage/auth/login/')
def compo_browse(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get compos
    compos = Compo.objects.filter(event_id=int(sel_event_id))
    
    # Form handling
    if request.method == "POST":
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_compo'):
            raise Http403
        
        # Handle form
        compoform = AdminCompoForm(request.POST)
        if compoform.is_valid():
            data = compoform.save(commit=False)
            data.event_id = int(sel_event_id)
            data.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/compos/') 
    else:
        compoform = AdminCompoForm()
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_browse.html", {
        'compos': compos,
        'compoform': compoform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def compo_edit(request, sel_event_id, compo_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_compo'):
        raise Http403
    
    # Get compo
    compo = get_object_or_404(Compo, pk=compo_id)
    
    # Handle form
    if request.method == "POST":
        editform = AdminCompoForm(request.POST, instance=compo)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/compos/') 
    else:
        editform = AdminCompoForm(instance=compo)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/compo_edit.html", {
        'compo': compo,
        'editform': editform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def entry_browse(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Form handling
    if request.method == "POST":
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_entry'):
            raise Http403
        
        # Handle form
        entryform = AdminEntryAddForm(request.POST, request.FILES)
        if entryform.is_valid():
            entryform.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/entries/') 
    else:
        entryform = AdminEntryAddForm()
    
    # Get Entries    
    compos = Compo.objects.filter(event=int(sel_event_id))
    entries = Entry.objects.filter(compo__in=compos)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_browse.html", {
        'entries': entries,
        'entryform': entryform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def entry_edit(request, sel_event_id, entry_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_entry'):
        raise Http403
    
    # Check ID
    entry = get_object_or_404(Entry, pk=entry_id)
    
    # Handle form
    if request.method == "POST":
        editform = AdminEntryForm(request.POST, request.FILES, instance=entry)
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/entries/') 
    else:
        editform = AdminEntryForm(instance=entry)
    
    # Render response
    return admin_render(request, "admin_kompomaatti/entry_edit.html", {
        'entry': entry,
        'editform': editform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def results(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get compos
    compos = Compo.objects.filter(event_id=int(sel_event_id))

    # Get the entries
    results = {}
    for compo in compos:
        results[compo.name] = entrysort.sort_by_score(Entry.objects.filter(compo=compo))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/results.html", {
        'results': results,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def votecodes(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
        
    # Handle form
    if request.method == 'POST':
        # CHeck for permissions
        if not request.user.has_perm('kompomaatti.add_votecode'):
            raise Http403
        
        # Handle form
        gentokensform = CreateTokensForm(request.POST)
        if gentokensform.is_valid():
            amount = int(gentokensform.cleaned_data['amount'])
            for n in range(amount):
                try:
                    c = VoteCode()
                    c.event_id = int(sel_event_id)
                    c.key = unicode(hashlib.md5(str(random.random())).hexdigest()[:8])
                    c.save()
                except IntegrityError:
                    n = n-1 # Ugly, may cause infinite loop...
            return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/votecodes/') 
    else:
        gentokensform = CreateTokensForm()
        
    # Get tokens
    tokens = VoteCode.objects.filter(event_id=int(sel_event_id))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/votecodes.html", {
        'tokens': tokens,
        'gentokensform': gentokensform,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required(login_url='/manage/auth/login/')
def votecodes_print(request, sel_event_id):
    # Make sure the user is superuser.
    if not request.user.is_staff:
        raise Http403
    
    # Get free votecodes
    codes = VoteCode.objects.filter(event_id=int(sel_event_id), associated_to=None)
    
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
    
@login_required(login_url='/manage/auth/login/')
def votecoderequests(request, sel_event_id):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Get all requests
    requests = VoteCodeRequest.objects.filter(event_id=int(sel_event_id))
    
    # Render response
    return admin_render(request, "admin_kompomaatti/vcrequests.html", {
        'requests': requests,
        'selected_event_id': int(sel_event_id),
    })
    
@login_required
def votecoderequests_accept(request, sel_event_id, vcrid):
    # Make sure the user is staff
    if not request.user.is_staff:
        raise Http403
    
    # CHeck for permissions
    if not request.user.has_perm('kompomaatti.change_votecode'):
        raise Http403
    
    # Get the request
    vcr = get_object_or_404(VoteCodeRequest, pk=vcrid)
        
    # Add votecode for user. Bang your head to the wall until you succeed, etc.
    # TODO: Do something about this shit!
    done = False
    for i in range(25):
        try:
            c = VoteCode()
            c.event_id = int(sel_event_id)
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
    return HttpResponseRedirect('/manage/'+sel_event_id+'/kompomaatti/votecoderequests/') 

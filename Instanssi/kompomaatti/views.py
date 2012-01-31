# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from models import Compo, Entry, Vote, VoteCode, VoteCodeRequest
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404, HttpResponseRedirect, HttpResponse
from forms import EntryForm, CreateTokensForm, VoteCodeAssocForm, RequestVoteCodeForm
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from datetime import datetime
from Instanssi.kompomaatti.misc import awesometime
from operator import itemgetter
import random
import hashlib
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

# ---- HELPER FUNCTIONS ----
def custom_render(request, tpl, context={}):
    context['compos'] = Compo.objects.filter(active=True)
    context['logged'] = request.user.is_authenticated()
    context['is_su'] = request.user.is_superuser
    associated = False
    votecode = None
    try:
        votecode = VoteCode.objects.get(associated_to=request.user)
        associated = True
    except:
        pass
    context['associated'] = associated
    context['votecode'] = votecode
    return render_to_response(tpl, context, context_instance=RequestContext(request))

def compo_times_formatter(compo):
    compo.compo_time = awesometime.format_single(compo.compo_start)
    compo.adding_time = awesometime.format_single(compo.adding_end)
    compo.editing_time = awesometime.format_single(compo.editing_end)
    compo.voting_time = awesometime.format_between(compo.voting_start, compo.voting_end)
    return compo

# ---- PAGES ----

def index(request):
    return custom_render(request, 'kompomaatti/index.html')

def help(request):
    return custom_render(request, 'kompomaatti/help.html')

@login_required
def admin_printcodes(request):
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
        
    # Get data
    compos = Compo.objects.all()
    entries = Entry.objects.all()
    tokens = VoteCode.objects.all()
    vcreqs = VoteCodeRequest.objects.all()
        
    # Just dump the page
    return custom_render(request, 'kompomaatti/admin.html', {
        'tokens': tokens,
        'entries': entries,
        'compos': compos,
        'vcreqs': vcreqs,
        'gentokensform': gentokensform,
    })

@login_required
def admin_givecode(request, vcrid):
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
        raise HttpResponse("Virhe yritettäessä lisätä satunnaista avainta ... FIXME!")
            
    # Delete request
    vcr.delete()
    
    # Return to admin page
    return HttpResponseRedirect('/kompomaatti/admin/') 

@login_required
def myentries(request): 
    # Get list of users entries
    my_entries = Entry.objects.filter(user=request.user)
    
    # Get list of open compos, format times
    open_compos = Compo.objects.filter(active=True, adding_end__gte = datetime.now())
    oclist = []
    for compo in open_compos:
        formatted_compo = compo_times_formatter(compo)
        oclist.append(formatted_compo)

    # Check if we got data from vote code assoc form
    if request.method == 'POST' and request.POST['formtype'] == 'votecodeassocform':
        assocform = VoteCodeAssocForm(request.POST)
        if assocform.is_valid():
            code = assocform.cleaned_data['code']
            try:
                vc = VoteCode.objects.get(key=code)
                vc.associated_to = request.user
                vc.time = datetime.now()
                vc.save()
            except VoteCode.DoesNotExist:
                pass
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        assocform = VoteCodeAssocForm()
    
    # Get last VoteCodeRequest, if it exists
    try:
        vcreq = VoteCodeRequest.objects.get(user=request.user)
    except VoteCodeRequest.DoesNotExist:
        vcreq = None
    
    # Check if we got data from vote code request form
    if request.method == 'POST' and request.POST['formtype'] == 'requestvotecodeform':
        requestform = RequestVoteCodeForm(request.POST)
        if requestform.is_valid():
            if vcreq:
                vcreq.text = requestform.cleaned_data['text']
                vcreq.save()
            else:
                req = requestform.save(commit=False)
                req.user = request.user
                req.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        if vcreq:
            requestform = RequestVoteCodeForm(instance=vcreq)
        else:
            requestform = RequestVoteCodeForm()
        
    # Dump the page to the user
    return custom_render(request, 'kompomaatti/myentries.html', {
        'myentries': my_entries,
        'opencompos': oclist,
        'user': request.user,
        'assocform': assocform,
        'requestform': requestform,
    })

@login_required
def delentry(request, entry_id):
    # Check if entry exists and get the object
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404

    # Make sure the user owns the entry
    if entry.user != request.user:
        raise Http404    

    # Make sure the compo is active and if adding time is open
    if not entry.compo.active or entry.compo.editing_end < datetime.now():
        raise Http404
    
    # Delete entry and associated files
    if entry.entryfile:
        entry.entryfile.delete()
    if entry.sourcefile:
        entry.sourcefile.delete()
    if entry.imagefile_original:
        entry.imagefile_original.delete()
    entry.delete()
    
    # Redirect back to dashboard
    return HttpResponseRedirect('/kompomaatti/myentries/') 

@login_required
def addentry(request, compo_id):
    # Check if entry exists and get the object
    try:
        compo = Compo.objects.get(id=compo_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Make sure the compo is active and if adding time is open
    if not compo.active or compo.adding_end < datetime.now():
        raise Http404
    
    # Check if we got filled form
    if request.method == 'POST':
        addform = EntryForm(request.POST, request.FILES, compo=compo, legend="Uusi tuotos")
        if addform.is_valid():
            nentry = addform.save(commit=False)
            nentry.user = request.user
            nentry.compo = compo
            nentry.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        addform = EntryForm(compo=compo, legend="Uusi tuotos")

    # Return the edit form
    return custom_render(request, 'kompomaatti/addentry.html', {
        'addform': addform,
        'compo': compo,
    })

@login_required
def editentry(request, entry_id):
    # Check if entry exists and get the object
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Make sure the user owns the entry
    if entry.user != request.user:
        raise Http404
    
    # Make sure the compo is active and if adding time is open
    if not entry.compo.active or entry.compo.editing_end < datetime.now():
        raise Http404
    
    # Check if we got filled form    
    if request.method == 'POST':
        editform = EntryForm(request.POST, request.FILES, instance=entry, editing=True, compo=entry.compo, legend="Muokkaa tuotosta")
        if editform.is_valid():
            editform.save()
            return HttpResponseRedirect('/kompomaatti/myentries/') 
    else:
        editform = EntryForm(instance=entry, editing=True, compo=entry.compo, legend="Muokkaa tuotosta")
    
    # Return the edit form
    return custom_render(request, 'kompomaatti/editentry.html', {
        'editform': editform,
        'entry': entry,
    })

def compo(request, compo_id):
    # Get compo information
    try:
        c = Compo.objects.get(id=compo_id, active=True)
    except ObjectDoesNotExist:
        raise Http404
    
    # Format times and stuff
    c = compo_times_formatter(c)
    
    # The following is only relevant, if the user is logged in and valid.
    has_voted = False
    voting_open = False
    votes = {}
    if request.user.is_authenticated():
        # Check if user has already voted
        votes = Vote.objects.filter(user=request.user, compo=c).order_by('rank')
        if votes.count() > 0:
            has_voted = True
        
        # Check if voting is open
        now = datetime.now()
        if c.voting_start <= now and now < c.voting_end:
            voting_open = True
    
        # Check if we want to do something with forms and stuff.
        if request.method == 'POST':
            if voting_open:
                # Make sure the user has a valid votecode
                try:
                    votecode = VoteCode.objects.get(associated_to=request.user)
                except:
                    return HttpResponse("Ei äänestysoikeutta!")
                
                # Get entries in compo that are not disqualified
                compo_entries = Entry.objects.filter(compo=c, disqualified=False)
                
                # Get the input data, and format it so that we can handle it.
                # HTML mode and JS mode voting systems give out different kind 
                # of data
                order = []
                tmp = {}
                if request.POST['action'] == 'vote_html':
                    for entry in compo_entries:
                        check_for = "ventry_"+str(entry.id)
                        if not request.POST.has_key(check_for):
                            return HttpResponse("Virhe syötteen käsittelyssä!") 
                        try:
                            tmp[entry.id] = int(request.POST[check_for])
                        except:
                            return HttpResponse("Virhe syötteen käsittelyssä!")
                    order = sorted(tmp, key=tmp.get)
                else:
                    order_raw = request.POST.getlist('order[]')
                    for id in order_raw:
                        try:
                            order.append(int(id))
                        except:
                            return HttpResponse("Virhe syötteen käsittelyssä!")
                        
                # Remove old votes by this user, on this compo
                if has_voted:
                    Vote.objects.filter(user=request.user, compo=c).delete()
                
                # Check voting input for cheating :P
                # See if all entries have a rank.
                for entry in compo_entries:
                    if entry.id not in order:
                        return HttpResponse("Virhe syötteen käsittelyssä!")
                
                # See that we have the right amount of entries
                if len(order) != len(compo_entries):
                    return HttpResponse("Virhe syötteen käsittelyssä!")

                # Make sure that no entry is in the list twice
                checked_ids = []
                for entryid in order:
                    if entryid not in checked_ids:
                        checked_ids.append(entryid)
                    else:
                        return HttpResponse("Virhe syötteen käsittelyssä!")

                # Add new votes, if there were no errors
                number = 1
                for entry_id in order:
                    vote = Vote()
                    vote.user = request.user
                    vote.compo = c
                    vote.entry = Entry.objects.get(id=entry_id)
                    vote.rank = number
                    vote.save()
                    number += 1
                
                # Select response mode according to input 
                if request.POST['action'] == 'vote_html':
                    return HttpResponseRedirect('/kompomaatti/compo/'+compo_id+'/') 
                else:
                    return HttpResponse("0") # 0 = Success.
            else: # If voting is closed, just show 404. This shouldn't really happen ...
                raise Http404
    
    # Get entries.
    # If voting is open, and user has already voted, get the order of entries by previous voting
    # If voting is open, and user has NOT voted yet, get the entries in random order
    # Otherwise just get entries sorted by name
    # Make sure that no disqualified entries are included if voting is open. No need to vote for those ...
    if voting_open and has_voted:
        e = []
        # First go through the entries that have been voted for and add them to list.
        for vote in votes:
            if not vote.entry.disqualified:
                e.append(vote.entry)
                
        # Then, make sure to also show entries that have NOT been voted previously by the user 
        # (if entry has been added late)
        entries_tmp = Entry.objects.filter(compo=c,disqualified=False).order_by('?')
        for entry in entries_tmp:
            if entry not in e:
                e.append(entry)
    elif voting_open:
        e = Entry.objects.filter(compo=c,disqualified=False).order_by('?')
    else:
        e = Entry.objects.filter(compo=c).order_by('name')
    
    # Render the page. Ya, rly.
    return custom_render(request, 'kompomaatti/compo.html', {
        'compo': c,
        'entries': e,
        'voting_open': voting_open,
        'has_voted': has_voted
    })


def compolist(request):
    # Get compos, format times
    composet = Compo.objects.filter(active=True).order_by('compo_start')
    compos = []
    for compo in composet:
        compos.append(compo_times_formatter(compo))
    
    # Get entries in compos. If compo has been flagged to show voting results, 
    # then get those. Otherwise just show entries in alphabetical order (by entry name).
    entries = {}
    for compo in compos:
        if compo.show_voting_results:
            # Get entries
            entries_temp = {}
            for entry in Entry.objects.filter(compo=compo):
                entries_temp[entry.id] = {
                    'id': entry.id,
                    'creator': entry.creator,
                    'name': entry.name,
                    'score': 0.0,
                    'disqualified': entry.disqualified,
                }
                # Want to show disqualified entries dead last.
                if entry.disqualified:
                    entries_temp[entry.id]['score'] = -1.0
            
            # Get score for each entry. Score should be 0 for all disqualified entries, 
            # so just discard those. Also skip votes with rank = 0. (division by zero etc.) :P
            all_votes = Vote.objects.select_related(depth=1).filter(compo=compo)
            for vote in all_votes:
                if not vote.entry.disqualified or vote.rank > 0:
                    entries_temp[vote.entry.id]['score'] += (1.0 / vote.rank)
            
            # Sort entries by score, highest score first (of course).
            entries[compo.id] = sorted(entries_temp.values(), key=itemgetter('score'), reverse=True)
        else:
            # Just get entries in alphabetical order
            entries[compo.id] = Entry.objects.filter(compo=compo).order_by('name')

    # Return page
    return custom_render(request, 'kompomaatti/compolist.html', {
        'compolist': compos,
        'entries': entries
    })


def entry(request, entry_id):
    # Get the entry. Show 404 if it doesn't exist ...
    try:
        entry = Entry.objects.get(id=entry_id)
    except ObjectDoesNotExist:
        raise Http404
    
    # Init dict that tells what we should show in the entry view
    show = {
        'youtube': False,
        'image': False,
        'jplayer': False,
    }
    
    # Select which views can be shown
    state = entry.compo.entry_view_type
    if state == 1:
        if entry.youtube_url:
            show['youtube'] = True
        elif entry.imagefile_original:
            show['image'] = True
    elif state == 2:
        if entry.imagefile_original:
            show['image'] = True
    elif state == 3:
        if entry.can_use_jplayer():
            show['jplayer'] = True
        elif entry.imagefile_original:
            show['image'] = True
    
    # Render the template
    return custom_render(request, 'kompomaatti/entry.html', {
        'entry': entry,
        'show': show,
    })

def dologout(request):
    logout(request)
    return HttpResponseRedirect('/kompomaatti/') 

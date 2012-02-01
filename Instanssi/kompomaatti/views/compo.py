# -*- coding: utf-8 -*-

from django.http import Http404, HttpResponseRedirect, HttpResponse
from datetime import datetime

from Instanssi.kompomaatti.misc.custom_render import custom_render
from Instanssi.kompomaatti.misc.time_formatting import compo_times_formatter
from Instanssi.kompomaatti.models import Entry, Compo, Vote

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

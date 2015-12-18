# -*- coding: utf-8 -*-

from common.http import Http403
from common.auth import staff_access_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Event, VoteCodeRequest, Entry, Compo


@staff_access_required
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http403
    
    # Flag that tells if there are any important notices for the user
    important_flag = False
    
    # Check if there are any waiting votecode requests
    vcreqs = []
    events = Event.objects.all()
    for event in events:
        rcount = VoteCodeRequest.objects.filter(event=event).count()
        if rcount > 0:
            important_flag = True
            vcreqs.append({
                'count': rcount,
                'event_id': event.id,
                'event_name': event.name,
            })
            
    # Find disk usage for entries
    entries = Entry.objects.all()
    disk_usage = 0
    for entry in entries:
        try:
            disk_usage += entry.entryfile.size
            if entry.sourcefile:
                disk_usage += entry.sourcefile.size
            if entry.imagefile_original:
                disk_usage += entry.imagefile_original.size
            if entry.imagefile_thumbnail:
                disk_usage += entry.imagefile_thumbnail.size
            if entry.imagefile_medium:
                disk_usage += entry.imagefile_medium.size
        except OSError:
            pass
        except IOError:
            pass
            
    # Get some statistics
    stats = {
        'events': Event.objects.all().count(),
        'entries': Entry.objects.all().count(),
        'compos': Compo.objects.all().count(),
        'space_usage': disk_usage,
    }
            
    # Render response
    return admin_render(request, "admin_base/index.html", {
        'real_name': request.user.first_name + ' ' + request.user.last_name,
        'important_flag': important_flag,
        'vcreqs': vcreqs,
        'stats': stats,
    })

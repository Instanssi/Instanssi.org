# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_base.misc.auth_decorator import su_access_required
from Instanssi.kompomaatti.models import Entry
from django.conf import settings
import os

@su_access_required
def diskcleaner(request):
    ENTRYDIR = os.path.join(settings.MEDIA_ROOT, 'kompomaatti/entryfiles/')
    SOURCEDIR = os.path.join(settings.MEDIA_ROOT, 'kompomaatti/entrysources/')
    IMAGEDIR = os.path.join(settings.MEDIA_ROOT, 'kompomaatti/entryimages/')
    
    # Get entries
    entries = Entry.objects.all()
    db_efs = []
    db_sfs = []
    db_ifs = []
    for entry in entries:
        db_efs.append(os.path.basename(entry.entryfile.name))
        if entry.imagefile_original:
            db_ifs.append(os.path.basename(entry.imagefile_original.name))
        if entry.sourcefile:
            db_sfs.append(os.path.basename(entry.sourcefile.name))
    
    # Get all entryfiles
    orphan_entryfiles = []
    for file in os.listdir(ENTRYDIR):
        if file not in db_efs:
            ext_path = os.path.join(settings.MEDIA_URL,'kompomaatti/entryfiles/')+file
            loc_path = ENTRYDIR+file
            orphan_entryfiles.append({
                'path': ext_path, 
                'name': file, 
                'size': os.path.getsize(loc_path),
            })
    
    # Render response
    return admin_render(request, "admin_utils/diskcleaner.html", {
        'orphan_entryfiles': orphan_entryfiles,
    })
    
@su_access_required
def log(request):
    # Render response
    return admin_render(request, "admin_utils/log.html", {
    })
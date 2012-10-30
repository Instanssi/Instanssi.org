# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Profile
from django.contrib.auth.models import User
from Instanssi.admin_users.forms import UserCreationForm

@login_required(login_url='/manage/auth/login/')
def superusers(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Check form
    # TODO: GIVE SEPARATE RIGHTS TO STAFF
    if request.user.is_superuser:
        if request.method == "POST":
            addform = UserCreationForm(request.POST)
            if addform.is_valid():
                addform.save()
                return HttpResponseRedirect("/manage/users/superusers/")
        else:
            addform = UserCreationForm()
    else:
        addform = None
    
    # Get users
    users = User.objects.exclude(username="openiduser")
    
    # Render response
    return admin_render(request, "admin_users/supers.html", {
        'superusers': users,
        'addform': addform,
    })

@login_required(login_url='/manage/auth/login/')
def openid(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get users
    db_users = User.objects.filter(username="openiduser")
    
    # Create list
    users = []
    for user in db_users:
        # Get other information on the user
        try:
            profile = Profile.objects.get(user=user)
            otherinfo = profile.otherinfo
        except:
            otherinfo = u""
        
        # Append data
        users.append({
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'date_joined': user.date_joined,
            'last_login': user.last_login,
            'is_active': user.is_active,
            'otherinfo': otherinfo,
        })
    
    # Render response
    return admin_render(request, "admin_users/openid.html", {
        'openidusers': users,
    })
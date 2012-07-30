# -*- coding: utf-8 -*-

from django.shortcuts import render_to_response
from django.http import Http404,HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Profile
from django.contrib.auth.models import User
from Instanssi.admin_users.forms import UserCreationForm

@login_required(login_url='/control/auth/login/')
def index(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get users
    try:
        users = User.objects.exclude(username="openiduser")
    except:
        raise Http404
    
    # Render response
    return admin_render(request, "admin_users/index.html", {
        'superusers': users,
    })

@login_required(login_url='/control/auth/login/')
def addsuperuser(request):
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
                return HttpResponseRedirect("/control/users/")
        else:
            addform = UserCreationForm()
    else:
        addform = None
        
    # Render response
    return admin_render(request, "admin_users/addsu.html", {
        'addform': addform,
    })

@login_required(login_url='/control/auth/login/')
def openid(request):
    # Make sure the user is staff.
    if not request.user.is_staff:
        raise Http404
    
    # Get users
    try:
        db_users = User.objects.filter(username="openiduser")
    except:
        raise Http404
    
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
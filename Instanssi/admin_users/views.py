# -*- coding: utf-8 -*-

from common.http import Http403
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.kompomaatti.models import Profile
from django.contrib.auth.models import User
from Instanssi.admin_users.forms import UserCreationForm, UserEditForm
from Instanssi.admin_base.misc.auth_decorator import staff_access_required, su_access_required
from Instanssi.dblog.models import DBLogEntry

# Logging related
import logging
logger = logging.getLogger(__name__)

@staff_access_required
def index(request):
    return admin_render(request, "admin_users/index.html", {})

@staff_access_required
def log(request):
    # Render response
    return admin_render(request, "admin_users/log.html", {
        'entries': DBLogEntry.objects.all().order_by('-date'),
    })

@staff_access_required
def users(request):
    # Check form
    if request.user.is_superuser:
        if request.method == "POST":
            userform = UserCreationForm(request.POST)
            if userform.is_valid():
                userform.save()
                logger.info('User added.', extra={'user': request.user})
                return HttpResponseRedirect(reverse('manage-users:index'))
        else:
            userform = UserCreationForm()
    else:
        userform = None
    
    # Get users
    users = User.objects.exclude(username="arkisto")
    
    # Render response
    return admin_render(request, "admin_users/users.html", {
        'superusers': users,
        'userform': userform,
    })

@su_access_required
def edit(request, su_id):
    # Get user info and make sure it's not SU we're trying to edit
    user = get_object_or_404(User, pk=su_id)
    if user.is_superuser:
        raise Http403
    
    # Handle form
    if request.method == "POST":
        userform = UserEditForm(request.POST, instance=user)
        if userform.is_valid():
            userform.save()
            logger.info('User '+user.username+' edited.', extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-users:index'))
    else:
        userform = UserEditForm(instance=user)
    
    # Render response
    return admin_render(request, "admin_users/edit.html", {
        'userform': userform,
    })

@su_access_required
def delete(request, su_id):
    # Try to delete
    user = get_object_or_404(User, pk=su_id)
    if user.is_superuser or user.username == "arkisto":
        raise Http403
    else:
        logger.info('User '+user.username+' deactivated.', extra={'user': request.user})
        user.is_active = False
        user.save()

    # All done, redirect
    return HttpResponseRedirect(reverse('manage-users:index'))


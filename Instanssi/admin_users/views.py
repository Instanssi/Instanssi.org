# -*- coding: utf-8 -*-

from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.models import User
from oauth2_provider.models import Application

from Instanssi.common.http import Http403
from Instanssi.common.auth import staff_access_required, su_access_required
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_users.forms import UserCreationForm, UserEditForm, ApiApplicationForm
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
    user_list = User.objects.exclude(username="arkisto")
    
    # Render response
    return admin_render(request, "admin_users/users.html", {
        'superusers': user_list,
        'userform': userform,
    })


@staff_access_required
def apps(request):
    # Handle adding new apps
    if request.method == 'POST':
        add_form = ApiApplicationForm(request.POST, user=request.user)
        if add_form.is_valid():
            app = add_form.save()
            logger.info('Application %s created.', app.name, extra={'user': request.user})
            return HttpResponseRedirect(reverse('manage-users:apps'))
    else:
        add_form = ApiApplicationForm()

    # Apps owned by the current user
    m_apps = Application.objects.filter(user=request.user)

    # Get all applications for superusers only
    all_apps = None
    if request.user.is_superuser:
        all_apps = Application.objects.all()

    return admin_render(request, "admin_users/api_tokens.html", {
        'apps': m_apps,
        'add_form': add_form,
        'all_apps': all_apps
    })


@staff_access_required
def delete_app(request, app_id):
    try:
        q = Application.objects.get_queryset()
        if not request.user.is_superuser:
            q = q.filter(user=request.user)
        app = q.get(id=app_id)
        logger.info('Application %s deleted.', app.name, extra={'user': request.user})
        app.delete()
    except Application.DoesNotExist:
        pass
    return HttpResponseRedirect(reverse('manage-users:apps'))


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
            logger.info('User "{}" edited.'.format(user.username), extra={'user': request.user})
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
        logger.info('User "{}" deactivated.'.format(user.username), extra={'user': request.user})
        user.is_active = False
        user.save()

    # All done, redirect
    return HttpResponseRedirect(reverse('manage-users:users'))

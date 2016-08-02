# -*- coding: utf-8 -*-

from common.auth import staff_access_required
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_profile.forms import PasswordChangeForm, InformationChangeForm


@staff_access_required
def password(request):
    if request.method == "POST":
        pwform = PasswordChangeForm(request.POST, user=request.user)
        if pwform.is_valid():
            pwform.save()
            return HttpResponseRedirect(reverse('manage-profile:password'))
    else:
        pwform = PasswordChangeForm()
    
    # Render response
    return admin_render(request, "admin_profile/password.html", {
        'pwform': pwform,
    })


@staff_access_required
def profile(request):
    # Check form
    if request.method == "POST":
        profileform = InformationChangeForm(request.POST, instance=request.user)
        if profileform.is_valid():
            profileform.save()
            return HttpResponseRedirect(reverse("manage-profile:index"))
    else:
        profileform = InformationChangeForm(instance=request.user)
    
    # Render response
    return admin_render(request, "admin_profile/profile.html", {
         'profileform': profileform,
    })
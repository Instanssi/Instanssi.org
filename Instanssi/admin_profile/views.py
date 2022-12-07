from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from Instanssi.admin_base.misc.custom_render import admin_render
from Instanssi.admin_profile.forms import InformationChangeForm, PasswordChangeForm
from Instanssi.common.auth import staff_access_required


@staff_access_required
def password(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        password_form = PasswordChangeForm(request.POST, user=request.user)
        if password_form.is_valid():
            password_form.save()
            return HttpResponseRedirect(reverse("manage-profile:password"))
    else:
        password_form = PasswordChangeForm()

    return admin_render(request, "admin_profile/password.html", {"pwform": password_form})


@staff_access_required
def profile(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        profile_form = InformationChangeForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            return HttpResponseRedirect(reverse("manage-profile:index"))
    else:
        profile_form = InformationChangeForm(instance=request.user)

    return admin_render(request, "admin_profile/profile.html", {"profileform": profile_form})

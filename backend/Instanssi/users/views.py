from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from Instanssi.users.forms import ProfileForm
from Instanssi.users.models import User


@login_required
def profile_view(request: HttpRequest) -> HttpResponse:
    assert isinstance(request.user, User)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Profile updated successfully."))
            return redirect("users:profile")
    else:
        form = ProfileForm(instance=request.user)
    return render(request, "users/profile.html", {"form": form})

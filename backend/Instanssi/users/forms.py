from __future__ import annotations

from typing import Any

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms
from django.contrib import auth
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from Instanssi.common.misc import get_url_local_path
from Instanssi.users.models import User


class DjangoLoginForm(forms.Form):
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput)
    next = forms.CharField(widget=forms.HiddenInput)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.next_page: str = kwargs.pop("next", "")
        self.logged_user: User | None = None
        super(DjangoLoginForm, self).__init__(*args, **kwargs)
        self.fields["next"].initial = self.next_page
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("Login with credentials"),
                "username",
                "password",
                "next",
                ButtonHolder(Submit("submit", _("Login"))),
            )
        )

    def clean_next(self) -> str:
        return get_url_local_path(self.cleaned_data["next"])

    def clean(self) -> dict[str, Any] | None:
        # Make sure the user is valid
        cleaned_data = super(DjangoLoginForm, self).clean()

        if "username" in self.cleaned_data and "password" in self.cleaned_data:
            self.logged_user = auth.authenticate(
                username=self.cleaned_data["username"], password=self.cleaned_data["password"]
            )
            if not self.logged_user or self.logged_user.is_active is False:
                self.logged_user = None
                raise ValidationError(_("Invalid username or password!"))
        return cleaned_data

    def login(self, request: HttpRequest) -> None:
        auth.login(request, self.logged_user)


class ProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.pop("user", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                _("User profile"),
                "first_name",
                "last_name",
                "email",
                "otherinfo",
                ButtonHolder(Submit("submit-profile", _("Save"))),
            )
        )

        self.fields["first_name"].label = _("First name")
        self.fields["last_name"].label = _("Last name")
        self.fields["email"].label = _("Email")
        self.fields["email"].required = True
        self.fields["otherinfo"].label = _("Other contact info")
        self.fields["otherinfo"].help_text = _("Other contact information, e.g. IRC nick & network, etc.")
        self.fields["otherinfo"].required = False

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "otherinfo")

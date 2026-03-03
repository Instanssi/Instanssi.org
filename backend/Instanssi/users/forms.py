from __future__ import annotations

from typing import Any

from allauth.account.forms import (
    AddEmailForm,
    ChangePasswordForm,
    LoginForm,
    ResetPasswordForm,
    ResetPasswordKeyForm,
    SetPasswordForm,
    SignupForm,
)
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Column, Div, Layout, Row, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from Instanssi.users.models import LANGUAGE_CHOICES, User


class ProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        kwargs.pop("user", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.layout = Layout(
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            "language",
            "otherinfo",
            Div(Submit("submit-profile", _("Save")), css_class="text-end mt-2"),
        )

        self.fields["otherinfo"].label = _("Other contact info")
        self.fields["otherinfo"].help_text = _("Other contact information, e.g. IRC nick & network, etc.")
        self.fields["otherinfo"].required = False
        self.fields["otherinfo"].widget.attrs["rows"] = 3

    class Meta:
        model = User
        fields = ("first_name", "last_name", "language", "otherinfo")


class CrispyLoginForm(LoginForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Sign In"), css_class="w-100 mt-2"))
        if "remember" in self.fields:
            del self.fields["remember"]
        self.fields["login"].label = ""
        self.fields["password"].label = ""


class CrispySignupForm(SignupForm):  # type: ignore[misc]
    first_name = forms.CharField(max_length=150, required=False, label=_("First name"))
    last_name = forms.CharField(max_length=150, required=False, label=_("Last name"))
    language = forms.ChoiceField(
        choices=LANGUAGE_CHOICES,
        required=False,
        label=_("Language"),
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            "username",
            "email",
            Row(
                Column("password1", css_class="col-md-6"),
                Column("password2", css_class="col-md-6"),
            ),
            Row(
                Column("first_name", css_class="col-md-6"),
                Column("last_name", css_class="col-md-6"),
            ),
            "language",
            Submit("signup", _("Register"), css_class="w-100 mt-2"),
        )

    def signup(self, request: Any, user: User) -> None:
        user.language = self.cleaned_data.get("language", "")
        user.save(update_fields=["language"])


class CrispyResetPasswordForm(ResetPasswordForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Reset Password"), css_class="w-100 mt-2"))


class CrispyResetPasswordKeyForm(ResetPasswordKeyForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Set New Password"), css_class="w-100 mt-2"))


class CrispyChangePasswordForm(ChangePasswordForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Change Password"), css_class="w-100 mt-2"))


class CrispySetPasswordForm(SetPasswordForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", _("Set Password"), css_class="w-100 mt-2"))


class CrispyAddEmailForm(AddEmailForm):  # type: ignore[misc]
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.form_method = "post"
        self.helper.add_input(Submit("action_add", _("Add Email"), css_class="w-100 mt-2"))

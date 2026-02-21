from typing import Any

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit
from django import forms
from django.utils.translation import gettext_lazy as _

from Instanssi.users.models import User


class ProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    class Meta:
        model = User
        fields = ["first_name", "last_name", "language", "otherinfo"]
        labels = {
            "first_name": _("First name"),
            "last_name": _("Last name"),
            "language": _("Language"),
            "otherinfo": _("Other info"),
        }

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.template_pack = "bootstrap5"
        self.helper.layout = Layout(
            "first_name",
            "last_name",
            "language",
            "otherinfo",
            FormActions(Submit("submit", _("Save")), css_class="d-flex justify-content-end"),
        )

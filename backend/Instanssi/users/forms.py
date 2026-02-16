from __future__ import annotations

from typing import Any

from django import forms

from Instanssi.kompomaatti.models import Profile
from Instanssi.users.models import User


class ProfileForm(forms.ModelForm):  # type: ignore[type-arg]
    otherinfo = forms.CharField(
        widget=forms.Textarea(),
        label="Muut yhteystiedot",
        help_text="Muut yhteystiedot, mm. IRC-nick & verkko, jne.",
        required=False,
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.user: User | None = kwargs.pop("user", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

        # Find profile
        try:
            self.profile = Profile.objects.get(user=self.user)
        except Profile.DoesNotExist:
            self.profile = Profile(user=self.user, otherinfo="")
            self.profile.save()

        # Finnish labels
        self.fields["first_name"].label = "Etunimi"
        self.fields["last_name"].label = "Sukunimi"
        self.fields["email"].label = "Sähköposti"
        self.fields["email"].required = True
        self.fields["otherinfo"].initial = self.profile.otherinfo

    def save(self, commit: bool = True) -> User:
        super(ProfileForm, self).save()
        self.profile.otherinfo = self.cleaned_data["otherinfo"]
        self.profile.save()
        instance: User = self.instance
        return instance

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms

from Instanssi.ext_programme.models import ProgrammeEvent


class ProgrammeEventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ProgrammeEventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Tapahtuma",
                "event_type",
                "title",
                "description",
                "start",
                "end",
                "place",
                "presenters",
                "presenters_titles",
                "icon_original",
                "icon2_original",
                "email",
                "home_url",
                "twitter_url",
                "github_url",
                "facebook_url",
                "linkedin_url",
                "wiki_url",
                "active",
                ButtonHolder(Submit("submit", "Tallenna")),
            )
        )

    class Meta:
        model = ProgrammeEvent
        exclude = (
            "event",
            "icon_small",
        )

from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Fieldset, Layout, Submit
from django import forms

from Instanssi.kompomaatti.models import Event


class EventForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                "Tapahtuma", "name", "tag", "date", "mainurl", ButtonHolder(Submit("submit", "Tallenna"))
            )
        )

    class Meta:
        model = Event
        fields = ("name", "tag", "date", "mainurl")

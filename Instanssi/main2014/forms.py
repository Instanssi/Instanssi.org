# -*- coding: utf-8 -*-

from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from django.conf import settings
from Instanssi.main2014.models import ToimistoSuoritus


class ToimistoCodeForm(forms.Form):
    code = forms.CharField(max_length=15, label="Koodi", help_text="Syötä saamasi koodi tähän.")
    nick = forms.CharField(max_length=32, label="Agenttinimi", help_text="Syötä tähän oma agenttinimesi.")
    
    def __init__(self, *args, **kwargs):
        super(ToimistoCodeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Syötä koodi',
                'code',
                'nick',
                ButtonHolder (
                    Submit('submit', 'OK')
                )
            )
        )

    def clean_nick(self):
        nick = self.cleaned_data['nick']
        try:
            ToimistoSuoritus.objects.get(nick=nick)
            raise ValidationError('Agenttinimi on jo käytössä. Valitse toinen nimi!')
        except ToimistoSuoritus.DoesNotExist:
            return nick

    def clean_code(self):
        code = self.cleaned_data['code']
        if code != settings.MAIN2014_TOIMISTO_CODE:
            raise ValidationError('Virheellinen koodi!')
        return code

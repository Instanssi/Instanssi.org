# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from django.core.exceptions import ValidationError
from Instanssi.kompomaatti.models import Entry

class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(EntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Lisää entry',
                'user',
                'compo',
                'name',
                'creator',
                'description',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                'youtube_url',
                'archive_score',
                'archive_rank',
                'disqualified',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Entry
        fields = ('user','compo','name','creator','description','entryfile',
                  'sourcefile','imagefile_original','youtube_url','archive_score',
                  'archive_rank','disqualified')

# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Event, Competition

class AdminCompetitionForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompetitionForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Kilpailu',
                'name',
                'description',
                'participation_end',
                'start',
                'end',
                'score_type',
                'score_sort',
                'show_results',
                'hide_from_archive',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Competition
        exclude = ('event',)

class AdminCompoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminCompoForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Kompo',
                'name',
                'description',
                'adding_end',
                'editing_end',
                'compo_start',
                'voting_start',
                'voting_end',
                'entry_sizelimit',
                'source_sizelimit',
                'formats',
                'source_formats',
                'active',
                'show_voting_results',
                'entry_view_type',
                'hide_from_archive',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Compo
        exclude = ('event',)

class AdminEntryAddForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminEntryAddForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'user',
                'compo',
                'name',
                'description',
                'creator',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                'youtube_url',
                ButtonHolder (
                    Submit('submit', 'Lisää')
                )
            )
        )
        
    class Meta:
        model = Entry
        exclude = ('disqualified','disqualified_reason','imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

class AdminEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'compo',
                'user',
                'name',
                'description',
                'creator',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                'youtube_url',
                'disqualified',
                'disqualified_reason',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Entry
        exclude = ('imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

class CreateTokensForm(forms.Form):
    amount = forms.IntegerField(min_value=1, max_value=100, label=u"Määrä", help_text=u"Montako tokenia luodaan.")
    
    def __init__(self, *args, **kwargs):
        super(CreateTokensForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Generoi tokeneita',
                'amount',
                ButtonHolder (
                    Submit('submit', 'Generoi')
                )
            )
        )


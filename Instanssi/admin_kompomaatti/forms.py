# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Event

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

class AdminEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(AdminEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Tuotos',
                'compo',
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
        exclude = ('user','imagefile_thumbnail','imagefile_medium','archive_score','archive_rank')

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
        
class RequestVoteCodeForm(forms.ModelForm):
    formtype = forms.CharField(widget=forms.HiddenInput(),initial=u"requestvotecodeform")
    
    def __init__(self, *args, **kwargs):
        super(RequestVoteCodeForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Pyydä äänestysoikeutta',
                'text',
                'formtype',
                ButtonHolder (
                    Submit('submit', 'Pyydä äänestysoikeutta')
                )
            )
        )
        
    class Meta:
        model = VoteCodeRequest
        fields = ('text',)
        
class VoteCodeAssocForm(forms.Form):
    formtype = forms.CharField(widget=forms.HiddenInput(),initial=u"votecodeassocform")
    code = forms.CharField(max_length=8, label=u"Äänestyskoodi", help_text=u"Syötä saamasi äänestyskoodi tähän.")
    
    def __init__(self, *args, **kwargs):
        super(VoteCodeAssocForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Syötä äänestyskoodi',
                'code',
                'formtype',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            vc = VoteCode.objects.get(key=code)
        except VoteCode.DoesNotExist:
            raise ValidationError(u'Äänestyskoodia ei ole olemassa!')
        return code

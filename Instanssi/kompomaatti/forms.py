# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
import os

from Instanssi.kompomaatti.misc.sizeformat import sizeformat
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest

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
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Compo

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
        exclude = ('user','imagefile_thumbnail',)

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

class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.legend = kwargs.pop('legend', 'Entry')
        self.compo = kwargs.pop('compo', None)
        self.editing = kwargs.pop('editing', False)
        
        # Max sizes for filefields
        self.max_source_size = self.compo.source_sizelimit
        self.max_entry_size = self.compo.entry_sizelimit
        
        # Layout for uni-form ext.
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                self.legend,
                'name',
                'creator',
                'description',
                'entryfile',
                'sourcefile',
                'imagefile_original',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
        # Create the fields
        super(EntryForm, self).__init__(*args, **kwargs)
        
        # Give the entryfile and sourcefile fields a nicer help_text
        if self.compo:
            self.fields['entryfile'].help_text = u"Tuotospaketti. Sallitut tiedostoformaatit: " + self.compo.readable_entry_formats() + u'. Tiedoston maksimikoko on ' + sizeformat(self.max_entry_size) + '.'
            self.fields['sourcefile'].help_text = u"Lähdekoodipaketti. Sallitut tiedostoformaatit: " + self.compo.readable_source_formats() + u'. Tiedoston maksimikoko on ' + sizeformat(self.max_source_size) + '.'

        # If we are editing, then entryfile field is not required
        if self.editing:
            self.fields['entryfile'].required = False

    class Meta:
        model = Entry
        fields = ('name','creator','description','entryfile','sourcefile','imagefile_original')

    def field_size_ok(self, fname, limit):
        if self.cleaned_data[fname] == None:
            return True
        return (self.cleaned_data[fname].size < limit)

    def field_format_ok(self, fname, formatfield):
        if self.cleaned_data[fname] == None:
            return True
        allowed = formatfield.split('|')
        type = os.path.splitext(self.cleaned_data[fname].name)[1][1:]
        return (type in allowed)

    def clean_entryfile(self):
        if not self.field_size_ok("entryfile", self.max_entry_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on ' + sizeformat(self.max_entry_size) + '.')
        if not self.field_format_ok("entryfile", self.compo.formats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: ' + self.compo.readable_entry_formats() + '.')
        return self.cleaned_data['entryfile']
    
    def clean_sourcefile(self):
        if not self.field_size_ok("sourcefile", self.max_source_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on ' + sizeformat(self.max_source_size) + '.')
        if not self.field_format_ok("sourcefile", self.compo.source_formats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: ' + self.compo.readable_source_formats() + '.')
        return self.cleaned_data['sourcefile']

    def validate(self):
        if not self.compo.active:
            raise ValidationError(u'Kompo ei ole aktiivinen.')


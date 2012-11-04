# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
import os
from django.contrib.auth.models import User
from Instanssi.kompomaatti.misc.sizeformat import sizeformat
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Profile

class ProfileForm(forms.ModelForm):
    otherinfo = forms.CharField(widget=forms.Textarea(), label=u"Muut yhteystiedot", help_text=u"Muut yhteystiedot, mm. IRC-nick & verkko, jne.", required=False)
    
    def __init__(self, *args, **kwargs):
        # Init
        self.user = kwargs.pop('user', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # Find profile
        try:
            self.profile = Profile.objects.get(user=self.user)
        except:
            self.profile = Profile()
            self.profile.user = self.user
            self.profile.otherinfo = u""
        
        # Build form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Käyttäjäprofiili',
                'first_name',
                'last_name',
                'email',
                'otherinfo',
                ButtonHolder (
                    Submit('submit-profile', 'Tallenna')
                )
            )
        )
        
        # Finnish labels
        self.fields['first_name'].label = u"Etunimi"
        self.fields['last_name'].label = u"Sukunimi"
        self.fields['email'].label = u"Sähköposti"
        self.fields['otherinfo'].initial = self.profile.otherinfo
                
    def save(self):
        super(ProfileForm, self).save()
        self.profile.otherinfo = self.cleaned_data['otherinfo']
        self.profile.save()
        
    class Meta:
        model = User
        fields = ('first_name','last_name','email')
        
class VoteCodeRequestForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(VoteCodeRequestForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Pyydä äänestysoikeutta',
                'text',
                ButtonHolder (
                    Submit('submit-vcreq', 'Pyydä äänestysoikeutta')
                )
            )
        )
        
    class Meta:
        model = VoteCodeRequest
        fields = ('text',)
        
class VoteCodeAssocForm(forms.Form):
    code = forms.CharField(max_length=8, label=u"Äänestyskoodi", help_text=u"Syötä saamasi äänestyskoodi tähän.")
    
    def __init__(self, *args, **kwargs):
        # Init
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super(VoteCodeAssocForm, self).__init__(*args, **kwargs)
        
        # Build form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Syötä äänestyskoodi',
                'code',
                ButtonHolder (
                    Submit('submit-vcassoc', 'Tallenna')
                )
            )
        )
        
    def clean_code(self):
        code = self.cleaned_data['code']
        try:
            vc = VoteCode.objects.get(event=self.event, key=code)
        except VoteCode.DoesNotExist:
            raise ValidationError(u'Virheellinen koodi!')
        return code
    
    def save(self):
        print self.cleaned_data
        vc = VoteCode.objects.get(event=self.event, key=self.cleaned_data['code'])
        vc.associated_to = self.user
        vc.time = datetime.now()
        vc.save()

class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.compo = kwargs.pop('compo', None)
        self.editing = kwargs.pop('editing', False)
        
        # Max sizes for filefields
        self.max_source_size = self.compo.source_sizelimit
        self.max_entry_size = self.compo.entry_sizelimit
        
        # Layout for uni-form ext.
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Entry',
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

    def clean_imagefile_original(self):
        # Check image size
        max_image_size = 6*1024*1024
        if not self.field_size_ok("imagefile_original", max_image_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on ' + sizeformat(max_image_size) + '.')
        
        # Check image format
        imageformats = ['png','jpg','gif']
        type = os.path.splitext(self.cleaned_data["imagefile_original"].name)[1][1:]
        if not (type in allowed):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: ' + ', '.join(imageformats) + '.')
        
        # Done
        return self.cleaned_data['sourcefile']

    def validate(self):
        if not self.compo.active:
            raise ValidationError(u'Kompo ei ole aktiivinen.')


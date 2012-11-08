# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from django.core.exceptions import ValidationError
import os
from django.contrib.auth.models import User
from Instanssi.kompomaatti.misc.sizeformat import sizeformat
from Instanssi.kompomaatti.models import Compo, Entry, VoteCode, VoteCodeRequest, Profile, CompetitionParticipation
from django.core.urlresolvers import reverse

class OpenIDLoginForm(forms.Form):
    sps = forms.ChoiceField(
        label=u'Kirjautumispalvelu', 
        help_text=u'Muutamia yleisimpiä kirjautumispalvelimia.')
    openid_identifier = forms.URLField(
        widget=forms.TextInput(), 
        max_length=255, 
        required=True, 
        label=u'Osoite', 
        help_text=u'Kirjautumispalvelun osoite. Voit joko valita ylläolevasta valikosta tunnetun, tai käyttää omaasi.')
    next = forms.CharField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        # Init
        self.next = kwargs.pop('next', "")
        super(OpenIDLoginForm, self).__init__(*args, **kwargs)
        
        # Build form
        self.helper = FormHelper()
        self.helper.form_action = reverse('openid-login')
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'sps',
                'openid_identifier',
                'next',
                ButtonHolder (
                    Submit('submit-login', u'Kirjaudu')
                )
            )
        )
        
        # Initial values
        self.fields['next'].initial = self.next
        self.fields['sps'].choices = [
            ('https://www.google.com/accounts/o8/id', 'Google'),
            ('https://korppi.jyu.fi/openid/', 'Korppi'),
            ('https://me.yahoo.com', 'Yahoo'),
        ]
        self.fields['sps'].initial = 0
        self.fields['openid_identifier'].initial = 'https://www.google.com/accounts/o8/id'
        

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
        self.fields['email'].required = True
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
                    Submit('submit-vcreq', u'Pyydä äänestysoikeutta')
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

class ParticipationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(ParticipationForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'participant_name',
                ButtonHolder (
                    Submit('submit', u'Osallistu')
                )
            )
        )

    class Meta:
        model = CompetitionParticipation
        fields = ('participant_name',)

class EntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.compo = kwargs.pop('compo', None)
        
        # Max sizes for filefields
        self.max_source_size = self.compo.source_sizelimit
        self.max_entry_size = self.compo.entry_sizelimit
        self.max_image_size = 6 * 1024 * 1024
        self.imageformats = ['png','jpg']
        
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
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
        # Create the fields
        super(EntryForm, self).__init__(*args, **kwargs)
        
        # Give the entryfile and sourcefile fields a nicer help_text
        if self.compo:
            # Description for entryfile
            self.fields['entryfile'].help_text = \
                u"Tuotospaketti. Sallitut tiedostoformaatit: " \
                + self.compo.readable_entry_formats() \
                + u'. Tiedoston maksimikoko on ' \
                + sizeformat(self.max_entry_size) + '.'
                
            # Description for sourcefile
            self.fields['sourcefile'].help_text = \
                u"Lähdekoodipaketti. Sallitut tiedostoformaatit: " \
                + self.compo.readable_source_formats() \
                + u'. Tiedoston maksimikoko on ' \
                + sizeformat(self.max_source_size) + '.'
        
        # Description for imagefile
        self.fields['imagefile_original'].help_text = \
            u"Kuva teokselle. Tätä käytetään mm. arkistossa ja kompomaatin äänestysvaiheessa. Sallitut kuvaformaatit: " \
            + ', '.join(self.imageformats)  \
            + u'. Tiedoston maksimikoko on ' \
            + sizeformat(self.max_image_size) + '.'

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
        if self.cleaned_data['imagefile_original'] == None:
            return None
        
        # Check image size
        if not self.field_size_ok("imagefile_original", self.max_image_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on ' + sizeformat(self.max_image_size) + '.')
        
        # Check image format
        type = os.path.splitext(self.cleaned_data["imagefile_original"].name)[1][1:]
        if not (type in self.imageformats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: ' + ', '.join(self.imageformats) + '.')
        
        # Done
        return self.cleaned_data['imagefile_original']

    def validate(self):
        if not self.compo.active:
            raise ValidationError(u'Kompo ei ole aktiivinen.')


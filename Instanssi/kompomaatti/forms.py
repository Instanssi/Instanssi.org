# -*- coding: utf-8 -*-

import os
from datetime import datetime
from django import forms
from django.core.exceptions import ValidationError
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.kompomaatti.misc.sizeformat import sizeformat
from Instanssi.kompomaatti.models import Entry, VoteCode, VoteCodeRequest, CompetitionParticipation


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
            VoteCode.objects.get(event=self.event, key=code)
        except VoteCode.DoesNotExist:
            raise ValidationError(u'Virheellinen koodi!')
        return code
    
    def save(self):
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
                ButtonHolder(
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
        self.show_thumbnail_field = (self.compo.thumbnail_pref == 0 or self.compo.thumbnail_pref == 2)
        self.max_image_size = 6 * 1024 * 1024
        
        # Layout for uni-form ext.
        self.helper = FormHelper()
        
        # Fill the fieldset with the required fields
        fs = Fieldset(u'Entry')
        fs.fields.extend([
            'name',
            'creator',
            'description',
            'entryfile',
            'sourcefile'
        ])
        
        # Add thumbnail field if necessary
        if self.show_thumbnail_field:
            fs.fields.append('imagefile_original')  
            
        # Add submitbutton
        fs.fields.append(ButtonHolder(Submit('submit', u'Tallenna')))
        
        # Add fieldset to layout
        self.helper.layout = Layout(fs)
        
        # Create the fields
        super(EntryForm, self).__init__(*args, **kwargs)
        
        # Give the entryfile and sourcefile fields a nicer help_text
        if self.compo:
            # Description for entryfile
            self.fields['entryfile'].help_text = \
                u"Tuotospaketti. Sallitut tiedostoformaatit: {}. Tiedoston maksimikoko on  {}.".format(
                    self.compo.readable_entry_formats(), sizeformat(self.max_entry_size))

            # Description for sourcefile
            self.fields['sourcefile'].help_text = \
                u"Lähdekoodipaketti. Sallitut tiedostoformaatit: {}. Tiedoston maksimikoko on {}.".format(
                    self.compo.readable_source_formats(), sizeformat(self.max_source_size))
        
        # If we want to show thumbnail field, set description etc.
        # Otherwise delete field from form.
        if self.show_thumbnail_field:
            # Set thumbnail "field required" flag
            if self.compo.thumbnail_pref == 0:
                self.fields['imagefile_original'].required = True
            else:
                self.fields['imagefile_original'].required = False
            
            # Description for imagefile
            self.fields['imagefile_original'].help_text = \
                u"Kuva teokselle. Tätä käytetään mm. arkistossa ja kompomaatin äänestysvaiheessa. Sallitut " \
                u"kuvaformaatit: {}. Tiedoston maksimikoko on {}.".format(self.compo.readable_image_formats(),
                                                                          sizeformat(self.max_image_size))
        else:
            del self.fields['imagefile_original']

    class Meta:
        model = Entry
        fields = ('name', 'creator', 'description', 'entryfile', 'sourcefile', 'imagefile_original')

    def get_file_ext(self, fname):
        return os.path.splitext(self.cleaned_data[fname].name)[1][1:]

    def get_file_size(self, fname):
        return self.cleaned_data[fname].size

    def field_size_ok(self, fname, limit):
        return self.get_file_size(fname) <= limit

    def field_format_ok(self, fname, formatfield):
        return self.get_file_ext(fname) in formatfield.split('|')

    def clean_entryfile(self):
        # Check if entryfile is set
        if not self.cleaned_data['entryfile']:
            return None
        
        # Check entry file size
        if not self.field_size_ok("entryfile", self.max_entry_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on {}'
                                  .format(sizeformat(self.max_entry_size)))
        
        # Check entry file format
        if not self.field_format_ok("entryfile", self.compo.formats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: {}'
                                  .format(self.compo.readable_entry_formats()))
        
        # All done.
        return self.cleaned_data['entryfile']
    
    def clean_sourcefile(self):
        # Check if sourcefile is set
        if not self.cleaned_data['sourcefile']:
            return None
        
        # Check source file size
        if not self.field_size_ok("sourcefile", self.max_source_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on {}.'
                                  .format(sizeformat(self.max_source_size)))
        
        # Check source file format
        if not self.field_format_ok("sourcefile", self.compo.source_formats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: {}.'
                                  .format(self.compo.readable_source_formats()))
        
        # All done.
        return self.cleaned_data['sourcefile']

    def clean_imagefile_original(self):
        # Check if imagefile_original is set
        if not self.cleaned_data['imagefile_original']:
            return None
        
        # Check image size
        if not self.field_size_ok("imagefile_original", self.max_image_size):
            raise ValidationError(u'Tiedoston koko on liian suuri! Suurin sallittu koko on {}.'
                                  .format(sizeformat(self.max_image_size)))
        
        # Check image format
        if not self.field_format_ok("imagefile_original", self.compo.image_formats):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: {}.'
                                  .format(self.compo.readable_image_formats()))
        
        # Done
        return self.cleaned_data['imagefile_original']

    def validate(self):
        # Make sure compo is active
        if not self.compo.active:
            raise ValidationError(u'Kompo ei ole aktiivinen.')

    def save(self, commit=True):
        instance = super(EntryForm, self).save(commit=False)
        if self.compo.thumbnail_pref == 1:
            name = unicode('gth_'+os.path.basename(instance.entryfile.url))
            instance.imagefile_original.save(name, instance.entryfile, commit)
        if commit:
            instance.save()
        return instance

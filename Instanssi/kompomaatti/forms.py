# -*- coding: utf-8 -*-

from django.forms import ModelForm
from models import Compo, Entry
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from datetime import datetime
from Instanssi.kompomaatti.misc.sizeformat import sizeformat
from django.core.exceptions import ValidationError
import os

class EntryForm(ModelForm):
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


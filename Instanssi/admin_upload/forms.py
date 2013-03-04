# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from models import UploadedFile
import os
from django.core.exceptions import ValidationError
from Instanssi.kompomaatti.misc.sizeformat import sizeformat

class UploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Lataa',
                'description',
                'file',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    def field_format_ok(self, fname, allowed):
        type = os.path.splitext(self.cleaned_data[fname].name)[1][1:]
        return (type in allowed)

    def clean_file(self):
        # Check format
        allowed = ['png','jpg','gif','zip','rar','7z','gz','tar','bz2','odt','odp','doc','docx','pdf','txt','ppt','pptx','xls','xlsx']
        if not self.field_format_ok("file", allowed):
            raise ValidationError(u'Tiedostotyyppi ei ole sallittu. Sallitut formaatit: ' + ', '.join(allowed) + '.')
        
        # Return
        return self.cleaned_data['file']
        
    class Meta:
        model = UploadedFile
        fields = ('description','file')
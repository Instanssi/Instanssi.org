# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from models import UploadedFile

class UploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'',
                'description',
                'file',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = UploadedFile
        fields = ('description','file')
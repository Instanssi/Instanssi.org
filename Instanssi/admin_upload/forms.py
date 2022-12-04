from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from .models import UploadedFile
import os
from django.core.exceptions import ValidationError


class UploadForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(UploadForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                'Lataa',
                'description',
                'file',
                ButtonHolder(
                    Submit('submit', 'Tallenna')
                )
            )
        )

    def field_format_ok(self, fname, allowed):
        return os.path.splitext(self.cleaned_data[fname].name)[1][1:].lower() in allowed

    def clean_file(self):
        # Check format
        allowed = ['png', 'jpg', 'gif', 'zip', 'rar', '7z', 'gz', 'tar', 'bz2', 'odt', 'odp', 'doc', 'docx', 'pdf',
                   'txt', 'ppt', 'pptx', 'xls', 'xlsx']
        if not self.field_format_ok("file", allowed):
            raise ValidationError('Tiedostotyyppi ei ole sallittu. Sallitut formaatit: {}.'.format(', '.join(allowed)))

        # Return
        return self.cleaned_data['file']

    class Meta:
        model = UploadedFile
        fields = ('description', 'file')

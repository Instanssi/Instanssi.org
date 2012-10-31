# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.ext_blog.models import BlogEntry

class BlogEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Blogientry',
                'title',
                'text',
                'public',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = BlogEntry
        fields = ('title','text','public')
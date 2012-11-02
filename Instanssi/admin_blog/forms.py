# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.ext_blog.models import BlogEntry

class BlogEntryEditForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEntryEditForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Muokkaa blogientryä',
                'title',
                'text',
                'date',
                'public',
                ButtonHolder (
                    Submit('submit', 'Tallenna')
                )
            )
        )
        
    class Meta:
        model = BlogEntry
        fields = ('title','text','public','date')

class BlogEntryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(BlogEntryForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Lisää uusi blogientry',
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
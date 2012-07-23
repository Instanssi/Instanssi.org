# -*- coding: utf-8 -*-

from django import forms
from uni_form.helper import FormHelper
from uni_form.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.dbsettings.models import Setting

class SettingForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.group = kwargs.pop('group', u'')
        self.choices = kwargs.pop('choices', {})
        
        # Init
        super(SettingForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout()
        
        # Get settings in group
        settings = Setting.get_by_group(self.group)
        
        # Create fieldset for everything
        fs = Fieldset(u'Asetukset')

        # Add fields for settings
        for k,v in settings.iteritems():
            if k in self.choices:
                self.fields[k] = forms.TypedChoiceField(choices=self.choices[k], coerce=type(v))
            elif type(v) == bool:
                self.fields[k] = forms.BooleanField()
            elif type(v) == int:
                self.fields[k] = forms.IntegerField()
            else:
                self.fields[k] = forms.CharField(max_length=128) 
                
            self.fields[k].initial = v
            fs.fields.append(k)
        
        # Add buttonholder
        bh = ButtonHolder (
            Submit('submit', u'Tallenna')
        )
        fs.fields.append(bh)
        
        # Add fieldset to layout
        self.helper.layout.fields.append(fs)
        
    def set_label(self, name, label):
        self.fields[name].label = label
        
    def set_help_text(self, name, ht):
        self.fields[name].help_text = ht
        
    def save(self):
        for k,v in self.cleaned_data.iteritems():
            Setting.set(k, v, self.group)

                
# -*- coding: utf-8 -*-

from django.forms import ModelForm
from models import Entry

class AddEntryForm(ModelForm):
    class Meta:
        model = Entry
        fields = ('compo','name','creator','description','entryfile')
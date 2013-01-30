# -*- coding: utf-8 -*-

from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder
from Instanssi.tickets.models import Ticket
from Instanssi.store.models import StoreItem

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        super(TicketForm, self).__init__(*args, **kwargs)
        
        # Set choices
        items = []
        for item in StoreItem.objects.filter(event=self.event, delivery_type=1):
            items.append((item.id, item.name))
        self.fields['storeitem'].choices = items
        
        # Set form
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Fieldset(
                u'Lataa',
                'used',
                'storeitem',
                'owner_firstname',
                'owner_lastname',
                'owner_email',
                ButtonHolder (
                    Submit('submit', u'Tallenna')
                )
            )
        )
        
    class Meta:
        model = Ticket
        fields = ('storeitem','used','owner_firstname','owner_lastname','owner_email')